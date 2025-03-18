# 个人网站

## 功能特性

### 博客系统
- 博客列表展示
- 博客详情页面
  - Markdown 内容渲染
  - 文章目录导航
  - 分享功能（Twitter、LinkedIn）
  - 相关文章推荐
  - 作者信息展示
  - 移动端适配

## 技术栈
- Vue 3
- TypeScript
- Vite
- Vue Router
- Marked (Markdown 渲染)
- DOMPurify (HTML 净化)
- Day.js (日期处理)
- SCSS

## 开发指南

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 项目结构
```
personal-website/
├── src/
│   ├── views/
│   │   └── blog/
│   │       ├── BlogList.vue    # 博客列表页面
│   │       └── BlogDetail.vue  # 博客详情页面
│   ├── components/
│   ├── router/
│   ├── assets/
│   └── App.vue
├── public/
└── package.json
```

## 开发规范
- 使用 TypeScript 进行类型检查
- 遵循 Vue 3 组合式 API 最佳实践
- 组件和函数必须包含注释说明
- 保持代码整洁和模块化
- 确保移动端兼容性

## 更新日志
详见 [CHANGELOG.md](./changelog.md) 