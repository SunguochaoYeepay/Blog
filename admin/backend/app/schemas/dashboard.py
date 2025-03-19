from pydantic import BaseModel
from typing import List
from datetime import datetime

class StatisticsData(BaseModel):
    """统计数据"""
    total_articles: int
    total_likes: int
    total_views: int
    total_users: int

class ChartData(BaseModel):
    """图表数据"""
    dates: List[str]
    views: List[int]
    likes: List[int]

class ActivityItem(BaseModel):
    """活动项"""
    title: str
    time: datetime
    type: str
    user: str

class CategoryStats(BaseModel):
    """分类统计"""
    name: str
    value: int

class SystemStatus(BaseModel):
    """系统状态"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    uptime: float

class DashboardData(BaseModel):
    """仪表盘数据"""
    statistics: StatisticsData
    chart_data: ChartData
    recent_activities: List[ActivityItem]
    category_stats: List[CategoryStats]
    system_status: SystemStatus 