#!/usr/bin/env python3
import argparse
from app.database import SessionLocal
from app.models.user import User
from app.api.auth import verify_password, get_password_hash

def check_admin():
    """检查管理员账户信息"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("\n管理员用户信息：")
            print(f"用户名: {admin.username}")
            print(f"邮箱: {admin.email}")
            print(f"姓名: {admin.full_name}")
            print(f"部门: {admin.department}")
            print(f"角色: {admin.role}")
            print(f"是否激活: {admin.is_active}")
            
            # 验证默认密码
            test_password = "admin"
            is_password_correct = verify_password(test_password, admin.hashed_password)
            print(f"\n默认密码 'admin' 是否正确: {is_password_correct}")
        else:
            print("未找到管理员用户")
        
    except Exception as e:
        print(f"查询管理员用户失败: {str(e)}")
    finally:
        db.close()

def reset_password(new_password=None):
    """重置管理员密码"""
    if not new_password:
        new_password = "admin"
        
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            admin.hashed_password = get_password_hash(new_password)
            db.commit()
            print("\n管理员密码重置成功")
            print("新的登录凭据：")
            print(f"用户名: admin")
            print(f"密码: {new_password}")
        else:
            print("未找到管理员用户")
        
    except Exception as e:
        print(f"重置管理员密码失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='管理员账户管理工具')
    parser.add_argument('action', choices=['check', 'reset'], 
                      help='执行的操作: check (检查账户信息) 或 reset (重置密码)')
    parser.add_argument('--password', '-p', 
                      help='设置新密码 (仅在 reset 操作时有效)')
    
    args = parser.parse_args()
    
    if args.action == 'check':
        check_admin()
    elif args.action == 'reset':
        reset_password(args.password)

if __name__ == "__main__":
    main() 