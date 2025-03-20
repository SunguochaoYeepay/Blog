import pytest
from sqlalchemy.orm import Session
from app.initial_data import init_db
from app.models.user import User

def test_init_db(db_session: Session):
    """测试初始化数据库"""
    init_db(db_session)
    
    # 验证超级管理员用户是否创建
    admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    assert admin is not None
    assert admin.is_superuser is True
    assert admin.is_active is True