# 用户和文章管理系统

一个基于 Vue.js 和 FastAPI 构建的全栈网络应用，用于管理用户和文章。

## 功能特性

### 用户管理
- 用户注册和身份验证
- 用户角色管理（管理员、编辑、普通用户）
- 用户资料管理
- 部门组织管理

### 文章管理
- 文章创建和编辑
- 分类和标签管理
- 文章状态管理
- 评论系统
- 浏览量和点赞统计

## 技术栈

### 前端
- Vue 3
- Vite
- Ant Design Vue
- Vue Router
- Axios

### 后端
- FastAPI
- SQLAlchemy
- PyMySQL
- Alembic（数据库迁移）
- JWT 认证

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### 后端设置
1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 设置数据库：
   ```bash
   alembic upgrade head
   ```

5. 启动后端服务器：
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 前端设置
1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run dev
   ```

## API 文档
- 当后端服务器运行时，可以在 `http://localhost:8000/docs` 访问 API 文档。

## 开发状态
- [x] 用户 CRUD 操作
- [x] 认证和授权
- [x] 文章管理
- [x] 分类和标签管理
- [x] 评论系统
- [ ] 文件上传和管理
- [ ] 用户活动追踪
- [ ] 高级搜索功能

## 许可证
本项目采用 MIT 许可证。 