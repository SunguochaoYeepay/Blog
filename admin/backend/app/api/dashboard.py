from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.dashboard import (
    DashboardData,
    StatisticsData,
    ChartData,
    ActivityItem,
    CategoryStats,
    SystemStatus
)
from app.services.dashboard import DashboardService

router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取仪表盘完整数据
    """
    service = DashboardService(db)
    return await service.get_dashboard_data()

@router.get("/dashboard/statistics", response_model=StatisticsData)
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取统计数据
    """
    service = DashboardService(db)
    return await service.get_statistics()

@router.get("/dashboard/chart", response_model=ChartData)
async def get_chart_data(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取图表数据
    """
    service = DashboardService(db)
    return await service.get_chart_data(days)

@router.get("/dashboard/activities", response_model=List[ActivityItem])
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取最近活动
    """
    service = DashboardService(db)
    return await service.get_recent_activities(limit)

@router.get("/dashboard/categories", response_model=List[CategoryStats])
async def get_category_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类统计
    """
    service = DashboardService(db)
    return await service.get_category_stats()

@router.get("/dashboard/system", response_model=SystemStatus)
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取系统状态
    """
    service = DashboardService(db)
    return await service.get_system_status()