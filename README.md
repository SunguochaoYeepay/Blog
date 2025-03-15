# Blog 博客系统

[English Documentation](README_en.md)

一个使用 FastAPI 和 Vue.js 构建的现代化博客应用，具有清晰美观的响应式设计。

## 功能特点

- 🚀 现代化技术栈：FastAPI（后端）+ Vue 3（前端）
- 🎨 基于 Ant Design Vue 的精美界面
- 🔐 基于 JWT 的身份认证
- 📝 文章的完整 CRUD 操作
- 🎯 RESTful API 设计
- 🔍 文章搜索和过滤
- 📱 全设备响应式设计

## 技术栈

### 后端
- FastAPI - 高性能 Web 框架
- SQLAlchemy - SQL 工具包和 ORM
- PyMySQL - MySQL 数据库适配器
- Python-Jose - JWT 令牌处理
- Passlib - 密码哈希
- Redis - 缓存
- Uvicorn - ASGI 服务器

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型安全的 JavaScript
- Ant Design Vue - UI 组件库
- Vue Router - Vue.js 官方路由
- Vite - 下一代前端构建工具

## 项目结构

```
Blog/
├── backend/                # 后端项目目录
│   ├── app/               # 应用代码
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置
│   │   ├── crud/         # 数据库操作
│   │   ├── db/           # 数据库配置
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── utils/        # 工具函数
│   ├── tests/            # 测试文件
│   └── requirements.txt   # Python 依赖
│
└── frontend/             # 前端项目目录
    ├── src/             # 源代码
    │   ├── api/        # API 调用
    │   ├── assets/     # 静态资源
    │   ├── components/ # Vue 组件
    │   ├── router/     # 路由配置
    │   ├── store/      # 状态管理
    │   └── views/      # 页面视图
    ├── public/         # 公共文件
    └── package.json    # Node.js 依赖
```

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows 系统：.\venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 设置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入数据库凭证和其他设置
```

5. 运行服务器：
```bash
uvicorn app.main:app --reload
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

## 功能列表

### 用户功能
- [x] 用户注册
- [x] 用户登录
- [ ] 密码重置
- [ ] 个人资料管理
- [ ] 头像上传

### 文章功能
- [x] 创建文章
- [x] 编辑文章
- [x] 删除文章
- [x] 文章列表
- [x] 文章详情
- [ ] 文章分类
- [ ] 文章标签
- [ ] 文章评论

### 管理功能
- [x] 文章管理
- [ ] 用户管理
- [ ] 评论管理
- [ ] 系统设置

## 开发规范

### Git 提交规范
- feat: 新功能
- fix: 修复 Bug
- docs: 文档变更
- style: 代码格式调整
- refactor: 代码重构
- test: 测试用例变更
- chore: 其他变更

### 代码规范
- 后端遵循 PEP 8 规范
- 前端遵循 ESLint 配置
- 使用 TypeScript 类型注解
- 组件使用 Composition API

## API 文档

后端服务器运行后，可以访问：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 开发中的功能

- [ ] 评论系统
- [ ] 文章分类和标签
- [ ] 高级搜索功能
- [ ] 用户资料管理
- [ ] 图片上传和管理
- [ ] 文章数据分析

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情