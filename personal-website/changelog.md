# Changelog

## [Unreleased]

### Added
- 新增博客详情页面 (BlogDetail.vue)
  - 支持 Markdown 内容渲染
  - 添加文章目录导航
  - 实现文章分享功能
  - 添加相关文章推荐
  - 支持移动端响应式布局
  - 优化代码展示样式
  - 中文化界面文本

### Changed
- 更新博客文章的数据结构，添加作者信息和分类标签
- 优化文章日期显示格式为中文格式

### Technical
- 使用 marked 进行 Markdown 渲染
- 使用 DOMPurify 进行 HTML 内容净化
- 使用 dayjs 处理日期格式化
- 添加 TypeScript 类型定义
- 优化代码结构和组件复用性 