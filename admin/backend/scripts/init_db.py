import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal, Base, engine
from app.initial_data import init_db

def init():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建初始数据
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    print("开始初始化数据库...")
    init()
    print("数据库初始化完成！") 