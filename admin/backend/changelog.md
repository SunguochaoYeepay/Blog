# Changelog

## [Unreleased]

### Added
- 在 SystemStatus 模型中添加了 uptime 字段
- 在系统状态 API 中添加了系统启动时间的获取功能
- 添加了统一的管理员账户管理工具 (admin_cli.py)

### Changed
- 修复了 dashboard 相关的测试用例
- 优化了系统状态数据的获取方式
- 删除了重复的 main.py，统一使用 run.py 作为启动入口
- 合并了 check_admin.py 和 reset_admin_password.py 到 admin_cli.py

### Removed
- 删除了本地文件上传相关配置和目录，完全迁移到七牛云存储
- 移除了 uploads 目录和相关的本地存储代码 