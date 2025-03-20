from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class StatisticsData(BaseModel):
    """统计数据模型"""
    total_users: int
    total_articles: int
    total_views: int
    total_likes: int

class ChartData(BaseModel):
    """图表数据模型"""
    dates: List[str]
    views: List[int]
    likes: List[int]

class ActivityItem(BaseModel):
    """活动项模型"""
    title: str
    time: datetime
    type: str
    user: str

class CategoryStats(BaseModel):
    """分类统计模型"""
    name: str
    value: int

class SystemStatus(BaseModel):
    """系统状态模型"""
    # CPU信息
    cpu_percent: float
    cpu_count: int
    cpu_freq: float  # MHz

    # 内存信息
    memory_percent: float
    memory_total: int  # bytes
    memory_available: int  # bytes
    memory_used: int  # bytes

    # 磁盘信息
    disk_percent: float
    disk_total: int  # bytes
    disk_free: int  # bytes
    disk_used: int  # bytes

    # 运行时间
    uptime_days: int
    uptime_hours: int
    uptime_minutes: int

    # 系统负载
    load_avg_1: float
    load_avg_5: float
    load_avg_15: float

class DashboardData(BaseModel):
    """仪表盘完整数据模型"""
    statistics: StatisticsData
    chart_data: ChartData
    recent_activities: List[ActivityItem]
    category_stats: List[CategoryStats]
    system_status: SystemStatus

class Dashboard(Base):
    """仪表盘统计数据模型"""
    __tablename__ = "dashboard_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 基础统计
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    total_articles: Mapped[int] = mapped_column(Integer, default=0)
    total_views: Mapped[int] = mapped_column(Integer, default=0)
    total_likes: Mapped[int] = mapped_column(Integer, default=0)
    
    # 图表数据
    chart_data: Mapped[dict] = mapped_column(JSON)  # 存储图表数据的JSON
    
    # 系统状态
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0)
    memory_percent: Mapped[float] = mapped_column(Float, default=0.0)
    disk_percent: Mapped[float] = mapped_column(Float, default=0.0)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)