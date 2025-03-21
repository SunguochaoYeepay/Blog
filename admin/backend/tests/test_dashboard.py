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

def test_dashboard_time_range_stats(db_session):
    """测试仪表盘时间范围统计"""
    # 创建测试数据
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # 创建不同时间的文章
    articles = [
        Article(
            title=f"Test Article {i}",
            slug=f"test-article-{i}",
            content=f"Test Content {i}",
            author_id=user.id,
            created_at=datetime(2024, 1, i+1)  # 2024年1月1日到9日
        ) for i in range(9)
    ]
    db_session.add_all(articles)
    db_session.commit()

    # 测试不同时间范围的统计
    time_range_stats = {
        "daily": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
            "expected_count": 3
        },
        "weekly": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "expected_count": 7
        },
        "monthly": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "expected_count": 9
        }
    }

    for range_type, data in time_range_stats.items():
        stats = DashboardData(
            statistics=StatisticsData(
                total_users=1,
                total_articles=len(articles),
                total_views=0,
                total_likes=0
            ),
            chart_data=ChartData(
                dates=[data["start_date"]],
                views=[0],
                likes=[0]
            ),
            recent_activities=[],
            category_stats=[],
            system_status=None,
            time_range=range_type,
            start_date=data["start_date"],
            end_date=data["end_date"]
        )

        assert stats.statistics.total_articles == data["expected_count"]

def test_dashboard_trend_analysis(db_session):
    """测试仪表盘趋势分析"""
    # 创建测试数据
    user = User(
        username="trend_test_user",
        email="trend_test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # 创建不同时间和浏览量的文章
    articles = []
    for i in range(7):  # 创建7天的数据
        article = Article(
            title=f"Trend Article {i}",
            slug=f"trend-article-{i}",
            content=f"Trend Content {i}",
            author_id=user.id,
            created_at=datetime(2024, 1, i+1),
            views=i * 10,  # 递增的浏览量
            likes=i * 2   # 递增的点赞数
        )
        articles.append(article)
    db_session.add_all(articles)
    db_session.commit()

    # 创建趋势分析数据
    trend_data = DashboardData(
        statistics=StatisticsData(
            total_users=1,
            total_articles=len(articles),
            total_views=sum(a.views for a in articles),
            total_likes=sum(a.likes for a in articles)
        ),
        chart_data=ChartData(
            dates=["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07"],
            views=[0, 10, 20, 30, 40, 50, 60],
            likes=[0, 2, 4, 6, 8, 10, 12]
        ),
        recent_activities=[],
        category_stats=[],
        system_status=None
    )

    # 验证趋势数据
    assert trend_data.statistics.total_views == 210  # 0 + 10 + 20 + 30 + 40 + 50 + 60
    assert trend_data.statistics.total_likes == 42   # 0 + 2 + 4 + 6 + 8 + 10 + 12
    assert len(trend_data.chart_data.dates) == 7
    assert len(trend_data.chart_data.views) == 7
    assert len(trend_data.chart_data.likes) == 7
    
    # 验证增长趋势
    views = trend_data.chart_data.views
    for i in range(1, len(views)):
        assert views[i] > views[i-1]  # 确保浏览量在增长

    likes = trend_data.chart_data.likes
    for i in range(1, len(likes)):
        assert likes[i] > likes[i-1]  # 确保点赞数在增长