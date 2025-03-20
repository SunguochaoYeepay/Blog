from fastapi import APIRouter, File, Depends
from fastapi.datastructures import UploadFile
from app.services.storage import storage_service
from app.api.deps import get_current_user
from app.schemas.response import Response
from app.models.user import User

router = APIRouter()

@router.post("/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    上传图片到七牛云
    
    Args:
        file: 图片文件
        current_user: 当前用户（通过token获取）
        
    Returns:
        dict: 包含图片URL等信息
    """
    result = await storage_service.upload_image(file)
    
    return Response(
        code=200,
        message="上传成功",
        data=result
    )