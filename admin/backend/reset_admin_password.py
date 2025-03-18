from app.database import SessionLocal
from app.models.user import User
from app.api.auth import get_password_hash

def reset_admin_password():
    db = SessionLocal()
    try:
        # 查询管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            # 重置密码为 "admin"
            admin.hashed_password = get_password_hash("admin")
            db.commit()
            print("管理员密码重置成功")
            print("新的登录凭据：")
            print("用户名: admin")
            print("密码: admin")
        else:
            print("未找到管理员用户")
        
    except Exception as e:
        print(f"重置管理员密码失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()