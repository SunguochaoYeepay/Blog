from fastapi import APIRouter
from app.schemas.response import Response

router = APIRouter(tags=["dashboard"])

@router.get("", response_model=Response)
def get_dashboard():
    """
    获取仪表盘数据
    """
    return Response(
        code=200,
        message="获取仪表盘数据成功",
        data={"dashboard_data": "示例数据"}
    )