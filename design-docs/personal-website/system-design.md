# 个人网站系统设计文档

## 1. 系统概述

本个人网站旨在打造一个现代化的个人展示平台，包含个人介绍、项目展示、博客系统等功能模块。采用 Vue3 + TypeScript 技术栈构建前端，FastAPI + MySQL 构建后端，注重用户体验、性能优化和代码质量。

## 2. 系统架构

### 2.1 技术栈选型
#### 2.1.1 前端技术栈
- 框架：Vue 3 + TypeScript + Vite
- 状态管理：Pinia
- 路由：Vue Router
- 样式：SCSS + CSS Modules
- UI 组件：自定义组件库
- 构建工具：Vite
- 代码规范：ESLint + Prettier

#### 2.1.2 后端技术栈
- 框架：FastAPI
- 数据库：MySQL
- ORM：SQLAlchemy
- 迁移工具：Alembic
- 认证：JWT
- 文档：Swagger/OpenAPI

### 2.2 目录结构
```
├── frontend/            # 前端项目
│   └── src/
│       ├── components/  # 全局通用组件
│       ├── views/       # 页面视图
│       ├── assets/      # 静态资源
│       ├── layouts/     # 布局组件
│       ├── router/      # 路由配置
│       ├── stores/      # 状态管理
│       ├── types/       # 类型定义
│       └── utils/       # 工具函数
│
└── backend/             # 后端项目
    ├── app/            # 应用主目录
    │   ├── api/       # API 路由
    │   ├── core/      # 核心配置
    │   ├── crud/      # 数据库操作
    │   ├── models/    # 数据库模型
    │   └── schemas/   # 数据验证模型
    ├── alembic/       # 数据库迁移
    ├── tests/         # 测试用例
    └── logs/          # 日志文件
```

## 3. 功能模块

### 3.1 主页模块（已实现）
- Hero 区域：个人介绍和主要技能展示
- Projects 区域：项目作品展示
- Contact 区域：联系方式和社交媒体链接

### 3.2 博客模块
#### 3.2.1 已实现功能
- 文章详情页面
  - Markdown 渲染
  - 代码块语法高亮
  - 响应式布局
  - 文章元信息展示

#### 3.2.2 待实现功能
- 文章列表页
  - 分类筛选
  - 标签系统
  - 搜索功能
  - 分页支持
- 文章管理
  - Markdown 编辑器
  - 图片上传
  - 草稿保存
- 社交功能
  - 评论系统
  - 点赞功能
  - 分享功能

### 3.3 后端模块（已实现）
- 用户认证
  - JWT 认证
  - 权限控制
- 博客管理
  - 文章 CRUD
  - 分类管理
  - 标签管理
- 文件上传
  - 图片上传
  - 文件存储
- 数据库
  - 自动迁移
  - 数据备份

## 4. 数据结构设计

### 4.1 核心数据类型
```typescript
// 作者信息
interface Author {
  id: number
  name: string
  avatar: string
  bio: string
  social?: {
    github?: string
    twitter?: string
    linkedin?: string
  }
}

// 项目信息
interface Project {
  id: number
  title: string
  description: string
  image?: string
  link?: string
  tags: string[]
  featured: boolean
}

// 博客文章
interface BlogPost {
  id: number
  title: string
  content: string
  coverImage: string
  category: string
  tags: string[]
  date: string
  author: Author
  status: 'draft' | 'published'
}
```

### 4.2 后端数据模型
```python
# 用户模型
class User(Base):
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool

# 文章模型
class Article(Base):
    id: int
    title: str
    content: str
    cover_image: str
    category_id: int
    author_id: int
    status: str
    created_at: datetime
    updated_at: datetime

# 分类模型
class Category(Base):
    id: int
    name: str
    description: str

# 标签模型
class Tag(Base):
    id: int
    name: str
```

## 5. 性能优化计划

### 5.1 已实现
- 组件按需加载
- 路由懒加载
- 类型安全

### 5.2 待实现
- 图片懒加载和优化
- 静态资源缓存策略
- 首屏加载优化
- SSR/SSG 支持
- 代码分割优化

## 6. 安全性考虑

### 6.1 已实现
- HTML 内容净化
- XSS 防护
- 类型安全

### 6.2 待实现
- CSRF 防护
- 图片上传安全检查
- 评论内容过滤
- 访问频率限制
- 敏感信息加密

## 7. 开发规范

### 7.1 代码规范
- 使用 TypeScript 强类型
- 组件命名采用 PascalCase
- 文件命名采用 kebab-case
- 每个组件不超过 300 行
- 必要的注释和文档

### 7.2 Git 工作流
- 主分支：main
- 开发分支：develop
- 功能分支：feature/*
- 修复分支：hotfix/*
- 提交信息规范：conventional commits

## 8. 部署方案

### 8.1 开发环境
- 前端：Vite dev server
- 后端：FastAPI uvicorn
- 数据库：MySQL
- 接口文档：Swagger UI
- 热更新支持

### 8.2 生产环境（已实现）
- 前端部署
  - 静态资源：CDN
  - 服务器：Nginx
- 后端部署
  - 应用服务器：Uvicorn
  - 进程管理：Supervisor
  - 反向代理：Nginx
- 数据库部署
  - MySQL 主从配置
  - 定时备份策略
- 通用配置
  - HTTPS 证书：Let's Encrypt
  - 容器化：Docker Compose
  - CI/CD：GitHub Actions

## 9. 项目进度

### 9.1 第一阶段（当前）✅
- 项目基础架构搭建
- 主页基础功能实现
- 博客详情页实现

### 9.2 第二阶段（进行中）
- 博客列表页开发
- 后端 API 实现
- 评论系统集成

### 9.3 第三阶段（计划中）
- 用户系统开发
- SEO 优化
- 性能优化

### 9.4 第四阶段（计划中）
- 监控系统
- 数据分析
- 自动化部署

## 10. 维护计划

### 10.1 日常维护
- 依赖包更新
- 性能监控
- 错误日志收集
- 用户反馈处理

### 10.2 定期优化
- 代码质量审查
- 性能指标检测
- 安全漏洞扫描
- 文档更新 