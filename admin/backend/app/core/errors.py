"""统一的错误码和错误消息定义"""

class ErrorCode:
    """错误码定义
    
    HTTP 状态码规范说明：
    - 200: 表示成功
    - 400: 表示客户端请求参数错误
    - 401: 表示未认证或认证失败
    - 403: 表示未授权访问
    - 404: 表示请求的资源不存在
    - 409: 表示资源冲突（如已存在）
    - 413: 表示请求体过大
    - 415: 表示不支持的媒体类型
    - 422: 表示请求格式正确但语义错误
    - 500: 表示服务器内部错误
    """
    SUCCESS = 200  # 成功响应
    
    # 认证相关错误码
    UNAUTHORIZED = 401      # 未认证，需要登录
    INVALID_CREDENTIALS = 401  # 登录凭证无效
    INACTIVE_USER = 403     # 改为403，因为这是一个授权问题而不是参数错误
    
    # 权限相关错误码
    FORBIDDEN = 403         # 无权限访问
    COMMENT_FORBIDDEN = 403 # 无权限操作评论
    
    # 参数验证相关错误码
    PARAM_ERROR = 400           # 请求参数格式错误
    VALIDATION_ERROR = 400      # 请求参数验证失败
    STATS_DATE_INVALID = 400    # 统计日期格式错误
    STATS_TYPE_INVALID = 400    # 统计类型参数错误
    STATS_PERIOD_INVALID = 400  # 统计周期参数错误
    
    # 资源不存在相关错误码
    NOT_FOUND = 404                    # 通用资源不存在
    ARTICLE_NOT_FOUND = 404            # 文章不存在
    COMMENT_NOT_FOUND = 404            # 评论不存在
    COMMENT_PARENT_NOT_FOUND = 404     # 父评论不存在
    COMMENT_ARTICLE_NOT_FOUND = 404    # 评论的文章不存在
    CATEGORY_NOT_FOUND = 404           # 分类不存在
    TAG_NOT_FOUND = 404                # 标签不存在
    FILE_NOT_FOUND = 404               # 文件不存在
    
    # 资源冲突相关错误码（改为409）
    ARTICLE_ALREADY_EXISTS = 409    # 文章已存在，冲突
    ARTICLE_TITLE_EXISTS = 409      # 文章标题重复，冲突
    ARTICLE_SLUG_EXISTS = 409       # 文章别名重复，冲突
    ARTICLE_HAS_COMMENTS = 409      # 文章存在评论，删除操作冲突
    
    CATEGORY_ALREADY_EXISTS = 409   # 分类已存在，冲突
    CATEGORY_NAME_EXISTS = 409      # 分类名称重复，冲突
    CATEGORY_SLUG_EXISTS = 409      # 分类别名重复，冲突
    CATEGORY_HAS_ARTICLES = 409     # 分类下有文章，删除操作冲突
    
    TAG_ALREADY_EXISTS = 409        # 标签已存在，冲突
    TAG_NAME_EXISTS = 409           # 标签名称重复，冲突
    TAG_SLUG_EXISTS = 409           # 标签别名重复，冲突
    TAG_HAS_ARTICLES = 409          # 标签下有文章，删除操作冲突
    
    USER_ALREADY_EXISTS = 409       # 用户已存在，冲突
    USER_EMAIL_EXISTS = 409         # 邮箱已被使用，冲突
    USER_USERNAME_EXISTS = 409      # 用户名已被使用，冲突
    
    # 实体状态错误相关错误码（改为422）
    ARTICLE_STATUS_ERROR = 422      # 文章状态不允许当前操作
    COMMENT_STATUS_ERROR = 422      # 评论状态不允许当前操作
    USER_STATUS_ERROR = 422         # 用户状态不允许当前操作
    USER_ROLE_INVALID = 422         # 用户角色不符合业务规则
    
    # 文件上传相关错误码（使用更精确的状态码）
    INVALID_FILE_TYPE = 415         # 不支持的文件类型
    FILE_TOO_LARGE = 413           # 文件超出大小限制
    UPLOAD_ERROR = 500             # 文件上传服务器错误
    FILE_DELETE_ERROR = 500        # 文件删除服务器错误
    
    # 服务器错误
    SERVER_ERROR = 500             # 服务器内部错误

    # 文章相关错误码
    ARTICLE_CATEGORY_NOT_FOUND = 404  # 文章分类不存在
    ARTICLE_TAG_NOT_FOUND = 404  # 文章标签不存在
    ARTICLE_CONTENT_EMPTY = 400  # 文章内容为空
    
    # 评论相关错误码
    COMMENT_PARENT_NOT_FOUND = 404  # 父评论不存在
    COMMENT_CONTENT_EMPTY = 400  # 评论内容为空
    
    # 分类相关错误码
    CATEGORY_HAS_ARTICLES = 400  # 分类下有文章，无法删除
    CATEGORY_NAME_EXISTS = 400  # 分类名称已存在
    CATEGORY_SLUG_EXISTS = 400  # 分类别名已存在
    
    # 标签相关错误码
    TAG_HAS_ARTICLES = 400  # 标签下有文章，无法删除
    TAG_NAME_EXISTS = 400  # 标签名称已存在
    TAG_SLUG_EXISTS = 400  # 标签别名已存在
    
    # 用户相关错误码
    USER_EMAIL_EXISTS = 400  # 邮箱已存在
    USER_USERNAME_EXISTS = 400  # 用户名已存在
    USER_ROLE_INVALID = 400  # 用户角色无效

class ErrorMessages:
    """错误消息定义"""
    # 成功消息
    SUCCESS = "操作成功"
    LOGIN_SUCCESS = "登录成功"
    LOGOUT_SUCCESS = "退出登录成功"
    USER_INFO_SUCCESS = "获取用户信息成功"
    TOKEN_REFRESHED = "令牌刷新成功"
    PASSWORD_CHANGED = "密码修改成功"
    
    # 认证相关错误消息
    NOT_AUTHENTICATED = "未认证"
    INVALID_CREDENTIALS = "无效的凭证"
    INACTIVE_USER = "用户未激活"
    TOKEN_EXPIRED = "令牌已过期"
    INVALID_TOKEN = "无效的令牌"
    INVALID_REFRESH_TOKEN = "无效的刷新令牌"
    TOKEN_REFRESH_SUCCESS = "令牌刷新成功"
    
    # 权限相关错误消息
    FORBIDDEN = "无权限执行此操作"
    
    # 参数相关错误消息
    PARAM_ERROR = "参数错误"
    VALIDATION_ERROR = "验证错误"
    INVALID_PASSWORD = "无效的凭证"
    INVALID_PASSWORD_LENGTH = "密码长度不能小于8位"
    PASSWORD_CHANGE_SUCCESS = "密码修改成功"
    
    # 资源相关错误消息
    NOT_FOUND = "资源不存在"
    USER_NOT_FOUND = "用户不存在"
    
    # 服务器错误消息
    SERVER_ERROR = "服务器错误"

    # 文章相关错误消息
    ARTICLE_NOT_FOUND = "文章不存在"
    ARTICLE_ALREADY_EXISTS = "文章已存在"
    ARTICLE_TITLE_EXISTS = "文章标题已存在"
    ARTICLE_SLUG_EXISTS = "文章别名已存在"
    ARTICLE_CATEGORY_NOT_FOUND = "文章分类不存在"
    ARTICLE_TAG_NOT_FOUND = "文章标签不存在"
    ARTICLE_STATUS_ERROR = "文章状态错误"
    ARTICLE_CONTENT_EMPTY = "文章内容不能为空"
    ARTICLE_HAS_COMMENTS = "文章有评论，无法删除"
    ARTICLE_CREATE_SUCCESS = "文章创建成功"
    ARTICLE_UPDATE_SUCCESS = "文章更新成功"
    ARTICLE_DELETE_SUCCESS = "文章删除成功"
    ARTICLE_PUBLISH_SUCCESS = "文章发布成功"
    ARTICLE_UNPUBLISH_SUCCESS = "文章取消发布成功"
    ARTICLE_DRAFT_SUCCESS = "文章已保存为草稿"
    ARTICLE_ARCHIVE_SUCCESS = "文章已归档"
    ARTICLE_RESTORE_SUCCESS = "文章已恢复"
    
    # 评论相关错误消息
    COMMENT_NOT_FOUND = "评论不存在"
    COMMENT_FORBIDDEN = "无权限操作该评论"
    COMMENT_PARENT_NOT_FOUND = "父评论不存在"
    COMMENT_ARTICLE_NOT_FOUND = "评论的文章不存在"
    COMMENT_CONTENT_EMPTY = "评论内容不能为空"
    COMMENT_STATUS_ERROR = "评论状态错误"
    COMMENT_CREATE_SUCCESS = "评论发布成功"
    COMMENT_UPDATE_SUCCESS = "评论更新成功"
    COMMENT_DELETE_SUCCESS = "评论删除成功"
    COMMENT_APPROVE_SUCCESS = "评论审核通过"
    COMMENT_REJECT_SUCCESS = "评论审核拒绝"
    COMMENT_SPAM_SUCCESS = "评论已标记为垃圾评论"
    COMMENT_RESTORE_SUCCESS = "评论已恢复"
    
    # 分类相关错误消息
    CATEGORY_NOT_FOUND = "分类不存在"
    CATEGORY_ALREADY_EXISTS = "分类已存在"
    CATEGORY_HAS_ARTICLES = "分类下存在文章，无法删除"
    CATEGORY_NAME_EXISTS = "分类名称已存在"
    CATEGORY_SLUG_EXISTS = "分类别名已存在"
    CATEGORY_CREATE_SUCCESS = "分类创建成功"
    CATEGORY_UPDATE_SUCCESS = "分类更新成功"
    CATEGORY_DELETE_SUCCESS = "分类删除成功"
    CATEGORY_ORDER_SUCCESS = "分类排序更新成功"
    
    # 标签相关错误消息
    TAG_NOT_FOUND = "标签不存在"
    TAG_ALREADY_EXISTS = "标签已存在"
    TAG_HAS_ARTICLES = "标签下存在文章，无法删除"
    TAG_NAME_EXISTS = "标签名称已存在"
    TAG_SLUG_EXISTS = "标签别名已存在"
    TAG_CREATE_SUCCESS = "标签创建成功"
    TAG_UPDATE_SUCCESS = "标签更新成功"
    TAG_DELETE_SUCCESS = "标签删除成功"
    TAG_MERGE_SUCCESS = "标签合并成功"
    
    # 文件上传相关错误消息
    UPLOAD_ERROR = "文件上传失败"
    INVALID_FILE_TYPE = "不支持的文件类型"
    FILE_TOO_LARGE = "文件大小超出限制"
    FILE_DELETE_ERROR = "文件删除失败"
    UPLOAD_SUCCESS = "文件上传成功"

    # 仪表盘相关错误消息
    STATS_DATE_INVALID = "统计日期无效"
    STATS_TYPE_INVALID = "统计类型无效"
    STATS_PERIOD_INVALID = "统计周期无效"
    STATS_SUCCESS = "获取统计数据成功"

    # 用户相关错误消息
    USER_ALREADY_EXISTS = "用户已存在"
    USER_EMAIL_EXISTS = "邮箱已被使用"
    USER_USERNAME_EXISTS = "用户名已被使用"
    USER_ROLE_INVALID = "用户角色无效"
    USER_STATUS_ERROR = "用户状态错误"
    USER_CREATE_SUCCESS = "用户创建成功"
    USER_UPDATE_SUCCESS = "用户信息更新成功"
    USER_DELETE_SUCCESS = "用户删除成功"
    USER_ROLE_UPDATE_SUCCESS = "用户角色更新成功"
    USER_STATUS_UPDATE_SUCCESS = "用户状态更新成功" 