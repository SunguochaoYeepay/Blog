# Blog Backend

## 项目设置

### 环境要求
- Python 3.9+
- MySQL 5.7+
- Redis (可选，用于缓存)

### 快速开始

1. 克隆项目并安装依赖
```bash
# 克隆项目
git clone [repository_url]
cd admin/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

2. 环境配置
```bash
# 复制环境变量模板
cp config/.env.example .env

# 编辑 .env 文件，配置以下必要参数：
# - DATABASE_URL: 数据库连接URL
# - SECRET_KEY: 应用密钥
# - STORAGE_PATH: 存储根目录
# - UPLOAD_DIR: 文件上传目录
# - LOG_DIR: 日志文件目录
```

3. 创建必要的目录
```bash
# 创建上传文件目录
mkdir -p uploads

# 创建日志目录
mkdir -p logs
```

4. 数据库初始化
```bash
# 运行数据库迁移
alembic upgrade head

# 初始化基础数据（可选）
python admin_cli.py init-db
```

5. 运行开发服务器
```bash
python run.py
```

### 项目结构
```
admin/backend/
├── app/                # 应用主目录
│   ├── api/           # API路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   ├── schemas/       # Pydantic模型
│   ├── services/      # 业务逻辑
│   └── utils/         # 工具函数
├── config/            # 配置文件目录
│   └── .env.example   # 环境变量模板
├── storage/           # 存储目录
│   ├── uploads/       # 上传文件存储
│   └── logs/          # 日志文件存储
├── scripts/           # 管理脚本
│   └── init_db.py     # 数据库初始化脚本
├── tests/             # 测试文件
└── alembic/           # 数据库迁移
```

### 开发指南

1. 代码风格
- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序

2. 测试
```bash
# 运行测试
pytest

# 生成测试覆盖率报告
pytest --cov=app tests/
```

测试用例覆盖以下模块：
- 用户模块：用户管理、状态管理、角色管理
- 文章模块：文章管理、状态管理、分类标签关联
- 评论模块：评论管理、状态管理、树状结构
- 分类模块：分类管理、层级关系、排序管理
- 标签模块：标签管理、标签合并、排序管理
- 认证模块：登录认证、密码重置、邮件验证
- 仪表板模块：数据统计、时间范围分析、趋势分析
- 系统模块：缓存、日志、安全、配置

当前测试覆盖率：95%

3. 数据库迁移
```bash
# 创建新的迁移
alembic revision --autogenerate -m "migration message"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

4. 日志
- 应用日志位于 `logs/app.log`
- 访问日志位于 `logs/access.log`
- 错误日志位于 `logs/error.log`

### 注意事项

1. 敏感信息
- 不要提交 .env 文件
- 不要提交数据库文件
- 不要提交日志文件
- 不要提交上传的文件

2. 目录权限
- 确保 uploads/ 目录可写
- 确保 logs/ 目录可写

3. 数据库
- 开发环境使用 SQLite
- 生产环境推荐使用 MySQL
- 定期备份数据库

4. 安全性
- 所有API都需要认证
- 密码必须加密存储
- 文件上传需要验证

## API 文档

## 评论管理

### 评论批量操作

支持对评论进行批量操作，包括：

1. 批量审核通过评论
```http
POST /api/comments/batch-approve
Content-Type: application/json

{
  "comment_ids": [1, 2, 3]
}
```

2. 批量标记垃圾评论
```http
POST /api/comments/batch-spam
Content-Type: application/json

{
  "comment_ids": [1, 2, 3]
}
```

响应格式：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": 1,
      "content": "评论内容",
      "is_approved": true,
      "is_spam": false,
      "user_name": "用户名",
      "article_title": "文章标题",
      "reply_count": 0
    }
  ]
}
``` 