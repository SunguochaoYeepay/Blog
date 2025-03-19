from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.schemas.common import ResponseModel
from app.logger import setup_logger
from app.api.auth import get_current_user
from app.models.user import User
import mimetypes
from qiniu import Auth, put_data, BucketManager
from app.config import settings
import os
import uuid
from fastapi.responses import JSONResponse

logger = setup_logger("upload")
router = APIRouter()

# 支持的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_MIME_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/upload", response_model=ResponseModel[dict], status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件到七牛云
    
    Args:
        file: 要上传的文件
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含上传文件信息的响应
        
    Raises:
        HTTPException: 当上传失败时抛出异常
    """
    # 检查文件内容是否为空
    file_content = await file.read()
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseModel(
                code=status.HTTP_400_BAD_REQUEST,
                message="文件内容为空",
                data=None
            ).dict()
        )
    
    # 获取文件类型
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
    if not content_type or content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseModel(
                code=status.HTTP_400_BAD_REQUEST,
                message="不支持的文件类型",
                data=None
            ).dict()
        )

    # 确定文件类型
    if content_type in ALLOWED_IMAGE_TYPES:
        file_type = "image"
    else:
        file_type = "document"

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"

    try:
        # 初始化七牛云客户端
        q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        
        # 生成上传 Token
        token = q.upload_token(settings.QINIU_BUCKET_NAME)
        
        # 上传文件到七牛云
        ret, info = put_data(token, filename, file_content)
        
        if info.status_code == 200:
            # 生成文件访问 URL
            file_url = f"{settings.QINIU_DOMAIN}/{ret['key']}"
            
            # 返回文件信息
            return ResponseModel(
                code=status.HTTP_201_CREATED,
                message="文件上传成功",
                data={
                    "filename": filename,
                    "file_type": file_type,
                    "file_size": len(file_content),
                    "url": file_url
                }
            )
        else:
            raise Exception(f"七牛云上传失败: {info.error}")
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="文件上传失败",
                data=None
            ).dict()
        )

@router.get("/upload/files", response_model=ResponseModel[List[dict]], status_code=status.HTTP_200_OK)
async def list_files(
    file_type: Optional[str] = None,
    marker: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取七牛云存储空间中的文件列表
    
    Args:
        file_type: 可选的文件类型过滤
        marker: 上一次列举返回的位置标记，用于分页
        limit: 每次返回的最大条目数，默认100
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含文件列表的响应
        
    Raises:
        HTTPException: 当获取列表失败时抛出异常
    """
    try:
        # 初始化七牛云客户端
        q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        bucket = BucketManager(q)
        
        # 获取文件列表
        ret, eof, info = bucket.list(settings.QINIU_BUCKET_NAME, prefix=None, marker=marker, limit=limit)
        
        if info.status_code == 200:
            files = []
            for item in ret.get('items', []):
                file_info = {
                    'key': item['key'],
                    'hash': item['hash'],
                    'size': item['fsize'],
                    'mime_type': item['mimeType'],
                    'put_time': item['putTime'],
                    'url': f"{settings.QINIU_DOMAIN}/{item['key']}"
                }
                
                # 如果指定了文件类型，进行过滤
                if file_type:
                    if (file_type == 'image' and item['mimeType'] in ALLOWED_IMAGE_TYPES) or \
                       (file_type == 'document' and item['mimeType'] in ALLOWED_DOCUMENT_TYPES):
                        files.append(file_info)
                else:
                    files.append(file_info)
            
            return ResponseModel(
                code=status.HTTP_200_OK,
                message="获取文件列表成功",
                data={
                    'files': files,
                    'marker': ret.get('marker'),  # 用于下一次分页
                    'has_more': not eof  # 是否还有更多文件
                }
            )
        else:
            raise Exception(f"获取文件列表失败: {info.error}")
            
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="获取文件列表失败",
                data=None
            ).dict()
        )

@router.post("/upload/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> JSONResponse:
    """
    上传图片接口
    
    参数:
        file: 图片文件
        current_user: 当前登录用户
        
    返回:
        url: 图片访问地址
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}，仅支持: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 验证文件大小
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制: {len(contents)} bytes，最大允许: {MAX_IMAGE_SIZE} bytes"
        )
    
    try:
        # 初始化七牛云客户端
        q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}_{file.filename}"
        
        # 生成上传 Token
        token = q.upload_token(settings.QINIU_BUCKET_NAME)
        
        # 上传文件到七牛云
        ret, info = put_data(token, filename, contents)
        
        if info.status_code == 200:
            # 生成文件访问 URL
            file_url = f"{settings.QINIU_DOMAIN}/{ret['key']}"
            
            return JSONResponse({
                "code": 200,
                "message": "上传成功",
                "data": {
                    "url": file_url
                }
            })
        else:
            raise Exception(f"七牛云上传失败: {info.error}")
            
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="图片上传失败"
        ) 