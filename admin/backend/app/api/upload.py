from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime
from app.database import get_db
from app.schemas.common import ResponseModel
from app.logger import setup_logger
from app.api.auth import get_current_user
from app.models.user import User
import shutil
import mimetypes

logger = setup_logger("upload")
router = APIRouter()

# 支持的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_MIME_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

# 上传目录配置
UPLOAD_DIR = "uploads"
IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")
DOCUMENT_DIR = os.path.join(UPLOAD_DIR, "documents")

# 确保上传目录存在
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(DOCUMENT_DIR, exist_ok=True)

def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower()

def is_allowed_file(filename: str) -> bool:
    ext = get_file_extension(filename)
    for extensions in ALLOWED_EXTENSIONS.values():
        if ext in extensions:
            return True
    return False

def get_file_type(filename: str) -> str:
    ext = get_file_extension(filename)
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return "unknown"

@router.post("/upload", response_model=ResponseModel[dict], status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件"""
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
    
    # 重置文件指针
    await file.seek(0)
    
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

    # 确定文件类型和保存目录
    if content_type in ALLOWED_IMAGE_TYPES:
        file_type = "image"
        save_dir = IMAGE_DIR
    else:
        file_type = "document"
        save_dir = DOCUMENT_DIR

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(save_dir, filename)

    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="文件保存失败",
                data=None
            ).dict()
        )

    # 返回文件信息
    return ResponseModel(
        code=status.HTTP_201_CREATED,
        message="文件上传成功",
        data={
            "filename": filename,
            "file_type": file_type,
            "file_size": os.path.getsize(file_path),
            "file_path": file_path
        }
    )

@router.get("/upload/files", response_model=ResponseModel[List[dict]], status_code=status.HTTP_200_OK)
async def list_files(
    file_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文件列表"""
    try:
        files = []
        base_path = UPLOAD_DIR
        
        if file_type and file_type in ALLOWED_EXTENSIONS:
            base_path = os.path.join(base_path, file_type)
        
        for root, dirs, filenames in os.walk(base_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_info = {
                    "filename": filename,
                    "file_type": get_file_type(filename),
                    "file_size": os.path.getsize(file_path),
                    "upload_path": file_path,
                    "uploaded_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                files.append(file_info)
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data=files
        )
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=500,
                message="获取文件列表失败"
            ).dict()
        ) 