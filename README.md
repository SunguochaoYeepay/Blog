# Modern Blog System

一个现代化的博客系统，基于 FastAPI 和 Vue 3 构建，支持文章管理、分类、标签、评论等功能。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.3.4-4FC08D.svg?style=flat&logo=Vue.js&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2.0-3178C6.svg?style=flat&logo=TypeScript&logoColor=white)](https://www.typescriptlang.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=MySQL&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 功能特点

### 已实现功能

#### 用户系统 👥
- [x] 用户注册与登录
- [x] JWT 身份认证
- [x] 基于角色的权限控制
- [x] 用户信息管理
  - [x] 基本信息修改
  - [x] 头像上传
  - [x] 密码修改

#### 文章管理 📝
- [x] 文章 CRUD 操作
- [x] 文章分类管理
  - [x] 多级分类支持
  - [x] 分类排序
- [x] 文章标签管理
- [x] SEO 优化
  - [x] 自定义 meta 信息
  - [x] 友好的 URL slug

#### 评论系统 💬
- [x] 基础评论功能
- [x] 多级评论支持
- [x] 评论审核功能

#### 系统功能 ⚙️
- [x] 响应式布局
- [x] 数据库迁移
- [x] API 文档自动生成
- [x] 基本的错误处理
- [x] 日志记录

### 开发中功能 🚧

#### 内容增强
- [ ] Markdown 编辑器集成
- [ ] 文章版本控制
- [ ] 文章定时发布
- [ ] 文章导入/导出
- [ ] 文章模板

#### 用户体验
- [ ] 深色模式
- [ ] 国际化支持
- [ ] 自定义主题
- [ ] 快捷键支持

#### 互动功能
- [ ] 文章点赞
- [ ] 文章收藏
- [ ] 用户关注
- [ ] 文章分享
- [ ] 评论点赞

### 计划中功能 📋

#### 高级功能
- [ ] 全文搜索
  - [ ] ElasticSearch 集成
  - [ ] 搜索建议
  - [ ] 搜索历史
- [ ] 数据统计
  - [ ] 访问统计
  - [ ] 用户行为分析
  - [ ] 数据可视化
- [ ] 内容审核
  - [ ] AI 内容审核
  - [ ] 敏感词过滤
  - [ ] 反垃圾评论

#### 性能优化
- [ ] Redis 缓存集成
- [ ] 图片处理优化
  - [ ] 图片压缩
  - [ ] 图片 CDN
  - [ ] 懒加载
- [ ] 数据库优化
  - [ ] 读写分离
  - [ ] 分库分表

#### 安全增强
- [ ] CSRF 防护
- [ ] XSS 防护
- [ ] SQL 注入防护
- [ ] 请求限流
- [ ] 敏感数据加密

#### 运维功能
- [ ] Docker 部署支持
- [ ] CI/CD 流程
- [ ] 监控告警
- [ ] 自动备份
- [ ] 系统监控
  - [ ] 性能监控
  - [ ] 错误追踪
  - [ ] 用户行为追踪

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy
- **认证**: JWT
- **文档**: Swagger/OpenAPI
- **缓存**: Redis (计划中)

### 前端
- **框架**: Vue 3
- **类型**: TypeScript
- **状态管理**: Pinia
- **UI 框架**: Ant Design Vue
- **HTTP 客户端**: Axios
- **编辑器**: TipTap (计划中)

## 项目结构

```
Blog/
├── backend/           # 后端服务
│   ├── alembic/      # 数据库迁移
│   ├── app/          # 应用代码
│   │   ├── api/      # API 路由
│   │   ├── core/     # 核心功能
│   │   ├── models/   # 数据库模型
│   │   └── schemas/  # Pydantic 模型
│   └── tests/        # 测试用例
├── frontend/         # 前端应用
│   ├── src/
│   │   ├── api/     # API 接口
│   │   ├── components/  # 组件
│   │   ├── views/   # 页面
│   │   └── store/   # 状态管理
│   └── tests/       # 测试用例
└── design-docs/     # 设计文档
    ├── backend/     # 后端设计
    └── frontend/    # 前端设计
    
```

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+ (计划中)

### 后端设置

1. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库等信息
```

4. 运行数据库迁移
```bash
alembic upgrade head
```

5. 启动开发服务器
```bash
uvicorn app.main:app --reload
```

### 前端设置

1. 安装依赖
```bash
cd frontend
npm install
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置 API 地址等信息
```

3. 启动开发服务器
```bash
npm run dev
```

## API 文档

启动后端服务后，可以访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 部署

### Docker 部署 (计划中)
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 传统部署
详见 [部署文档](design-docs/backend/deployment.md)

## 开发指南

- [后端架构](design-docs/backend/architecture.md)
- [API 设计规范](design-docs/backend/api-standards.md)
- [数据库设计](design-docs/backend/database.md)
- [前端架构](design-docs/frontend/architecture.md)
- [前端代码规范](design-docs/frontend/code-standards.md)

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm run test
```

## 性能优化

- 数据库索引优化
- Redis 缓存层 (计划中)
- 前端资源懒加载
- CDN 加速 (计划中)
- 图片压缩和优化 (计划中)

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 更新日志

详见 [CHANGELOG.md](design-docs/changelog.md)

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 作者：Your Name
- 邮箱：your.email@example.com
- 项目链接：[https://github.com/yourusername/blog](https://github.com/yourusername/blog)

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Ant Design Vue](https://antdv.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)