import pytest
from datetime import datetime
from app.models.dashboard import DashboardData, StatisticsData, ChartData, ActivityItem, CategoryStats, SystemStatus
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment

def test_dashboard_stats(db_session):
    # 创建测试数据
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()  # 先提交用户
    
    article = Article(
        title="Test Article",
        slug="test-article",
        content="Test Content",
        author_id=user.id  # 使用用户的实际 ID
    )
    db_session.add(article)
    db_session.commit()  # 提交文章
    
    comment = Comment(
        content="Test Comment",
        article_id=article.id,  # 使用文章的实际 ID
        user_id=user.id  # 使用用户的实际 ID
    )
    db_session.add(comment)
    db_session.commit()  # 提交评论

    # 创建仪表盘数据
    stats = StatisticsData(
        total_users=1,
        total_articles=1,
        total_views=0,
        total_likes=0
    )

    chart_data = ChartData(
        dates=["2024-01-01"],
        views=[0],
        likes=[0]
    )

    activity = ActivityItem(
        title="New Article",
        time=datetime.now(),
        type="article",
        user="test@example.com"
    )

    category_stat = CategoryStats(
        name="Test Category",
        value=1
    )

    system_status = SystemStatus(
        cpu_percent=0.0,
        cpu_count=4,
        cpu_freq=2000.0,
        memory_percent=50.0,
        memory_total=8000000000,
        memory_available=4000000000,
        memory_used=4000000000,
        disk_percent=50.0,
        disk_total=100000000000,
        disk_free=50000000000,
        disk_used=50000000000,
        uptime_days=1,
        uptime_hours=0,
        uptime_minutes=0,
        load_avg_1=1.0,
        load_avg_5=1.0,
        load_avg_15=1.0
    )

    dashboard_data = DashboardData(
        statistics=stats,
        chart_data=chart_data,
        recent_activities=[activity],
        category_stats=[category_stat],
        system_status=system_status
    )

    # 验证数据
    assert dashboard_data.statistics.total_users == 1
    assert dashboard_data.statistics.total_articles == 1
    assert isinstance(dashboard_data.recent_activities[0].time, datetime)
    assert dashboard_data.category_stats[0].name == "Test Category"