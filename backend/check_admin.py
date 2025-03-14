from app.database import SessionLocal
from app.models.user import User
from app.api.auth import verify_password

def check_admin_user():
    db = SessionLocal()
    try:
        # 查询管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("管理员用户信息：")
            print(f"用户名: {admin.username}")
            print(f"邮箱: {admin.email}")
            print(f"姓名: {admin.full_name}")
            print(f"部门: {admin.department}")
            print(f"角色: {admin.role}")
            print(f"是否激活: {admin.is_active}")
            
            # 验证密码
            test_password = "admin"
            is_password_correct = verify_password(test_password, admin.hashed_password)
            print(f"\n密码 '{test_password}' 是否正确: {is_password_correct}")
        else:
            print("未找到管理员用户")
        
    except Exception as e:
        print(f"查询管理员用户失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()