from datetime import datetime
import os
import json
from typing import BinaryIO, Optional
from qiniu import Auth, put_data, etag
import qiniu.config
from fastapi import HTTPException
from fastapi.datastructures import UploadFile
from app.core.config import settings
import requests

class StorageService:
    """七牛云存储服务"""
    
    def __init__(self):
        self.auth = None
        self.bucket_name = None
        self.domain = None
        self.bucket_domain = None
        
        # 检查必要的配置是否存在
        if not all([
            settings.QINIU_ACCESS_KEY,
            settings.QINIU_SECRET_KEY,
            settings.QINIU_BUCKET_NAME,
            settings.QINIU_DOMAIN
        ]):
            print("Warning: 七牛云配置不完整，上传功能将不可用")
            return
            
        self.auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        self.bucket_name = settings.QINIU_BUCKET_NAME
        self.domain = settings.QINIU_DOMAIN
        self.bucket_domain = settings.QINIU_BUCKET_DOMAIN
        
        # 检查存储空间访问权限
        try:
            # 尝试直接访问一个不存在的文件
            test_url = f"{self.domain}/test_access_permission.txt"
            response = requests.head(test_url, verify=False)
            # 如果返回 403，说明是私有空间
            if response.status_code == 403:
                print("Warning: 当前存储空间是私有空间，请在七牛云控制台将其设置为公开空间")
        except requests.exceptions.RequestException as e:
            # 如果请求失败，记录错误但不影响服务启动
            print(f"Warning: Failed to check bucket access permission: {e}")

    def _generate_key(self, filename: str, prefix: str = 'images') -> str:
        """
        生成文件存储路径
        
        Args:
            filename: 原始文件名
            prefix: 文件路径前缀
            
        Returns:
            str: 存储路径
        """
        # 获取文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        # 生成日期路径
        date_path = datetime.now().strftime("%Y%m/%d")
        # 生成唯一文件名
        unique_filename = f"{datetime.now().strftime('%H%M%S')}{ext}"
        # 返回完整路径
        return f"{prefix}/{date_path}/{unique_filename}"

    def _validate_image(self, file: UploadFile):
        """
        验证图片文件
        
        Args:
            file: 上传的文件对象
            
        Raises:
            HTTPException: 当文件验证失败时抛出
        """
        # 验证文件类型
        if file.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}"
            )
        
        # 验证文件大小
        try:
            file_size = len(file.file.read())
            file.file.seek(0)  # 重置文件指针
            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE} bytes"
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"无法读取文件大小: {str(e)}"
            )

    async def upload_image(self, file: UploadFile, prefix: str = 'images') -> dict:
        """
        上传图片到七牛云
        
        Args:
            file: 上传的文件对象
            prefix: 存储路径前缀
            
        Returns:
            dict: 包含图片URL等信息
            
        Raises:
            HTTPException: 当上传失败时抛出
        """
        # 检查七牛云配置是否完整
        if not self.auth:
            raise HTTPException(
                status_code=500,
                detail="七牛云配置不完整，无法上传文件"
            )
            
        # 验证文件
        self._validate_image(file)
        
        try:
            # 读取文件内容
            contents = await file.read()
            
            # 生成存储路径
            key = self._generate_key(file.filename, prefix)
            
            # 生成上传凭证
            token = self.auth.upload_token(
                bucket=self.bucket_name,
                key=key,
                expires=3600,  # 凭证有效期：1小时
                policy={
                    'scope': f'{self.bucket_name}:{key}',
                    'deadline': 3600,  # 凭证有效期：1小时
                    'insertOnly': 1,  # 不允许覆盖同名文件
                    'fsizeLimit': settings.MAX_FILE_SIZE,  # 文件大小限制
                    'mimeLimit': ';'.join(settings.allowed_image_types),  # 文件类型限制
                    'fileType': 1,  # 标准存储
                    'callbackUrl': settings.QINIU_CALLBACK_URL,
                    'callbackBody': '{"key":"$(key)","hash":"$(etag)","size":$(fsize),"name":"$(fname)","type":"$(mimeType)"}',
                } if settings.QINIU_CALLBACK_URL else {
                    'scope': f'{self.bucket_name}:{key}',
                    'deadline': 3600,
                    'insertOnly': 1,
                    'fsizeLimit': settings.MAX_FILE_SIZE,
                    'mimeLimit': ';'.join(settings.allowed_image_types),
                    'fileType': 1,
                }
            )
            
            # 上传文件
            ret, info = put_data(
                up_token=token,
                key=key,
                data=contents,
                mime_type=file.content_type,
                check_crc=True
            )
            
            if info.status_code == 200:
                return {
                    'url': f'{self.domain}/{key}',  # CDN域名
                    'key': key,
                    'hash': ret['hash'],
                    'size': info.req_id,
                    'mime_type': file.content_type,
                    'original_name': file.filename
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"文件上传失败: {info.error}"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文件上传失败: {str(e)}"
            )
        finally:
            # 重置文件指针
            await file.seek(0)

storage_service = StorageService()