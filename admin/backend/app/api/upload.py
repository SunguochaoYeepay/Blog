from fastapi import APIRouter
from app.schemas.response import Response

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("", response_model=Response)
def upload_file():
    """
    上传文件
    """
    return Response(
        code=200,
        message="文件上传成功",
        data={"file_url": "示例URL"}
    )