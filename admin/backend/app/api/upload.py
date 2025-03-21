from fastapi import APIRouter, UploadFile, File, Depends
from app.schemas.response import Response
from app.services.storage import storage_service
from app.api import deps
from app.models.user import User

router = APIRouter(
    tags=["upload"]
)

@router.post("/image", response_model=Response)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    上传图片到七牛云
    """
    result = await storage_service.upload_image(file, prefix='articles')
    return Response(
        code=200,
        message="图片上传成功",
        data={"url": result['url']}
    )