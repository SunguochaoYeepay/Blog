import psutil
import time
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.models.article import Article
from app.models.comment import Comment
from app.models.user import User
from app.models.category import Category
from app.models.dashboard import (
    StatisticsData,
    ChartData,
    ActivityItem,
    CategoryStats,
    SystemStatus,
    DashboardData
)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    async def get_statistics(self) -> StatisticsData:
        """获取统计数据"""
        total_articles = self.db.query(func.count(Article.id)).scalar()
        total_likes = self.db.query(func.sum(Article.like_count)).scalar() or 0
        total_views = self.db.query(func.sum(Article.view_count)).scalar() or 0
        total_users = self.db.query(func.count(User.id)).scalar()

        return StatisticsData(
            total_articles=total_articles,
            total_likes=total_likes,
            total_views=total_views,
            total_users=total_users
        )

    async def get_chart_data(self, days: int = 30) -> ChartData:
        """获取图表数据"""
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 查询每天的文章浏览量和点赞数
        daily_stats = (
            self.db.query(
                func.date(Article.created_at).label('date'),
                func.sum(Article.view_count).label('views'),
                func.sum(Article.like_count).label('likes')
            )
            .filter(
                and_(
                    Article.created_at >= start_date,
                    Article.created_at <= end_date
                )
            )
            .group_by(func.date(Article.created_at))
            .all()
        )

        # 格式化数据并确保数据是按日期排序的
        stats_dict = {
            stat.date.strftime("%Y-%m-%d"): {
                'views': stat.views or 0,
                'likes': stat.likes or 0
            }
            for stat in daily_stats
        }

        # 生成完整的日期范围，确保没有数据的日期显示为0
        dates = []
        views = []
        likes = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(date_str)
            if date_str in stats_dict:
                views.append(stats_dict[date_str]['views'])
                likes.append(stats_dict[date_str]['likes'])
            else:
                views.append(0)
                likes.append(0)
            current_date += timedelta(days=1)

        return ChartData(
            dates=dates,
            views=views,
            likes=likes
        )

    async def get_recent_activities(self, limit: int = 10) -> List[ActivityItem]:
        """获取最近活动"""
        # 获取最近的文章
        recent_articles = (
            self.db.query(Article)
            .order_by(Article.created_at.desc())
            .limit(limit)
            .all()
        )

        activities = []
        for article in recent_articles:
            activities.append(
                ActivityItem(
                    title=article.title,
                    time=article.created_at,
                    type="article",
                    user=article.author.username
                )
            )

        return activities

    async def get_category_stats(self) -> List[CategoryStats]:
        """获取分类统计"""
        # 查询每个分类的文章数量
        category_counts = (
            self.db.query(Category)
            .join(Article.categories)
            .group_by(Category.id)
            .with_entities(
                Category.name,
                func.count(Article.id).label('count')
            )
            .all()
        )

        return [
            CategoryStats(name=cat.name, value=cat.count)
            for cat in category_counts
        ]

    async def get_system_status(self) -> SystemStatus:
        """获取系统状态"""
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)  # 1秒间隔采样
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0.0

        # 内存信息
        memory = psutil.virtual_memory()
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        
        # 计算运行时间
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_days = int(uptime_seconds // (24 * 3600))
        uptime_hours = int((uptime_seconds % (24 * 3600)) // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)

        # 系统负载
        try:
            load_avg = psutil.getloadavg()
        except (AttributeError, NotImplementedError):
            # Windows系统不支持getloadavg
            load_avg = (0.0, 0.0, 0.0)

        return SystemStatus(
            # CPU信息
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            cpu_freq=cpu_freq,
            
            # 内存信息
            memory_percent=memory.percent,
            memory_total=memory.total,
            memory_available=memory.available,
            memory_used=memory.used,
            
            # 磁盘信息
            disk_percent=disk.percent,
            disk_total=disk.total,
            disk_free=disk.free,
            disk_used=disk.used,
            
            # 运行时间
            uptime_days=uptime_days,
            uptime_hours=uptime_hours,
            uptime_minutes=uptime_minutes,
            
            # 系统负载
            load_avg_1=load_avg[0],
            load_avg_5=load_avg[1],
            load_avg_15=load_avg[2]
        )

    async def get_dashboard_data(self) -> DashboardData:
        """获取仪表盘数据"""
        statistics = await self.get_statistics()
        chart_data = await self.get_chart_data()
        recent_activities = await self.get_recent_activities()
        category_stats = await self.get_category_stats()
        system_status = await self.get_system_status()

        return DashboardData(
            statistics=statistics,
            chart_data=chart_data,
            recent_activities=recent_activities,
            category_stats=category_stats,
            system_status=system_status
        )