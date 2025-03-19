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
├── admin/             # 管理后台
│   ├── frontend/     # 管理后台前端
│   │   ├── src/     # 源代码
│   │   ├── tests/   # 测试用例
│   │   └── ...      # 其他配置文件
│   └── backend/     # 管理后台后端
│       ├── app/     # 应用代码
│       ├── tests/   # 测试用例
│       └── ...      # 其他配置文件
├── website/         # 前端网站
│   ├── src/        # 源代码
│   │   ├── components/  # 组件
│   │   ├── views/      # 页面
│   │   ├── stores/     # 状态管理
│   │   └── ...        # 其他代码
│   ├── tests/      # 测试用例
│   └── ...         # 其他配置文件
├── design-docs/    # 设计文档
│   ├── personal-website/  # 个人网站相关文档
│   └── boss-admin/       # 管理后台相关文档
└── ...            # 其他配置文件
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
cd admin/backend
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

#### 网站前端

1. 安装依赖

```bash
cd website
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

#### 管理后台前端

1. 安装依赖

```bash
cd admin/frontend
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

详见 [部署文档](design-docs/admin/backend/deployment.md)

## 开发指南

### 管理后台
- [后端架构](design-docs/admin/backend/architecture.md)
- [API 设计规范](design-docs/admin/backend/api-standards.md)
- [数据库设计](design-docs/admin/backend/database.md)
- [前端架构](design-docs/admin/frontend/architecture.md)
- [前端代码规范](design-docs/admin/frontend/code-standards.md)
- [部署指南](design-docs/admin/backend/deployment.md)

### 个人网站
- [前端架构](design-docs/website/architecture.md)
- [前端代码规范](design-docs/website/code-standards.md)
- [组件设计](design-docs/website/components.md)
- [性能优化](design-docs/website/performance.md)

### 通用文档
- [Git 工作流](design-docs/common/git-workflow.md)
- [代码审查规范](design-docs/common/code-review.md)
- [测试规范](design-docs/common/testing.md)
- [发布流程](design-docs/common/release-process.md)

## 测试

### 管理后台测试
#### 后端测试
```bash
cd admin/backend
pytest
```

#### 前端测试
```bash
cd admin/frontend
npm run test
```

### 网站前端测试
```bash
cd website
npm run test
```

## 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

详细指南请参考 [贡献指南](design-docs/common/contributing.md)

## 更新日志

详见 [CHANGELOG.md](changelog.md)

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息

## 作者

* **Your Name** - *Initial work* - [YourGithub](https://github.com/yourusername)

## 致谢

* 感谢所有为这个项目做出贡献的开发者
* 特别感谢 [FastAPI](https://fastapi.tiangolo.com/) 和 [Vue.js](https://vuejs.org/) 的开发团队

## 组件说明

### BaseList 基础列表页面组件

用于快速构建管理后台的列表页面，提供统一的布局和样式。

#### 功能特性

- 统一的搜索表单布局
- 灵活的表格操作区域
- 标准化的数据表格展示
- 统一的分页和加载状态
- 响应式布局支持

#### 使用示例

```vue
<template>
  <base-list
    :columns="columns"
    :data-source="dataList"
    :loading="loading"
    :pagination="pagination"
    @search="handleSearch"
    @reset="handleReset"
    @table-change="handleTableChange"
  >
    <!-- 搜索表单 -->
    <template #search-form>
      <a-form-item label="关键词">
        <a-input v-model:value="searchForm.keyword" />
      </a-form-item>
    </template>

    <!-- 表格操作区 -->
    <template #table-operations>
      <a-button type="primary">新建</a-button>
    </template>

    <!-- 自定义列内容 -->
    <template #column-content="{ column, record }">
      <!-- 自定义列渲染 -->
    </template>
  </base-list>
</template>
```