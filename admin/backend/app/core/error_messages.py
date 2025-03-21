"""统一的错误消息常量"""

class ErrorMessages:
    # 认证相关错误
    INVALID_CREDENTIALS = "用户名或密码错误"
    INACTIVE_USER = "用户未激活"
    NOT_AUTHENTICATED = "未经授权"
    TOKEN_EXPIRED = "令牌已过期"
    TOKEN_INVALID = "无效的令牌"
    TOKEN_MISSING = "未提供令牌"
    
    # 权限相关错误
    PERMISSION_DENIED = "权限不足"
    ROLE_REQUIRED = "需要特定角色"
    
    # 用户相关错误
    USER_NOT_FOUND = "用户不存在"
    USER_EXISTS = "用户已存在"
    EMAIL_EXISTS = "邮箱已被使用"
    
    # 操作相关错误
    OPERATION_FAILED = "操作失败"
    INVALID_REQUEST = "无效的请求"
    VALIDATION_ERROR = "数据验证错误"
    
    # 成功消息
    LOGIN_SUCCESS = "登录成功"
    LOGOUT_SUCCESS = "退出登录成功"
    PASSWORD_CHANGED = "密码修改成功"
    TOKEN_REFRESHED = "令牌刷新成功"
    USER_INFO_SUCCESS = "获取用户信息成功" 