# Blog System

一个基于 FastAPI 和 Vue.js 的博客系统。

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- Uvicorn

### 前端
- Vue 3
- TypeScript
- Ant Design Vue
- Vite

## 功能特性

- 文章管理
  - 创建、编辑、删除文章
  - 文章分类和标签
  - SEO 优化
  - 草稿和发布状态管理
  
- 评论系统
  - 评论管理
  - 垃圾评论过滤
  - 评论审核

- 用户系统
  - 用户管理
  - 角色权限

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/SunguochaoYeepay/Blog.git
cd Blog
```

2. 后端设置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 前端设置
```bash
cd frontend
npm install
```

4. 启动服务
```bash
# 在项目根目录
./run.sh all  # 启动所有服务
```

## API 文档

- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc

## 目录结构

```
.
├── backend/            # 后端代码
│   ├── app/           # 应用代码
│   │   ├── api/      # API 路由
│   │   ├── models/   # 数据模型
│   │   └── schemas/  # Pydantic 模型
│   └── requirements.txt
├── frontend/          # 前端代码
│   ├── src/
│   └── package.json
└── run.sh            # 启动脚本
``` 