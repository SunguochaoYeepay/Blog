# API 设计规范

## 基本原则

1. RESTful 设计
   - 使用标准 HTTP 方法
   - 资源命名使用名词复数形式
   - URL 使用小写字母，单词间用连字符分隔

2. 版本控制
   - 在 URL 中包含版本号：`/api/v1/`
   - 主版本号变更表示不兼容的 API 更改

3. 认证方式
   - 使用 Bearer Token
   - Token 在 Authorization 头中传递

## 请求格式

### HTTP 方法使用

- GET: 获取资源
- POST: 创建资源
- PUT: 更新资源（全量更新）
- PATCH: 更新资源（部分更新）
- DELETE: 删除资源

### URL 设计

```
# 列表资源
GET /api/v1/articles

# 特定资源
GET /api/v1/articles/{id}

# 子资源
GET /api/v1/articles/{id}/comments

# 资源操作
POST /api/v1/articles/{id}/publish
```

### 查询参数

1. 分页参数
```
?page=1&size=10
```

2. 排序参数
```
?sort=created_at&order=desc
```

3. 过滤参数
```
?status=published&category=tech
```

4. 搜索参数
```
?search=keyword
```

## 响应格式

### 成功响应

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "id": 1,
        "title": "示例文章",
        "content": "文章内容"
    }
}
```

### 列表响应

```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [{}, {}],
        "total": 100,
        "page": 1,
        "size": 10
    }
}
```

### 错误响应

```json
{
    "code": 400,
    "message": "请求参数错误",
    "data": null
}
```

## 状态码使用

- 200: 成功
- 201: 创建成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误

## 具体接口示例

### 用户认证

```
# 登录
POST /api/v1/auth/login
Request:
{
    "username": "string",
    "password": "string"
}
Response:
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "token": "string",
        "user": {}
    }
}
```

### 文章管理

```
# 创建文章
POST /api/v1/articles
Request:
{
    "title": "string",
    "content": "string",
    "category_id": "number",
    "tags": ["number"]
}
Response:
{
    "code": 200,
    "message": "创建成功",
    "data": {}
}

# 获取文章列表
GET /api/v1/articles?page=1&size=10
Response:
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [],
        "total": 0,
        "page": 1,
        "size": 10
    }
}
```

## 安全规范

1. 身份验证
   - 所有非公开 API 都需要验证
   - Token 过期时间设置合理
   - 敏感操作需要二次验证

2. 数据验证
   - 请求参数类型检查
   - 数据长度限制
   - 特殊字符过滤

3. 访问控制
   - 基于角色的权限控制
   - 资源所有者验证
   - 操作日志记录

## 性能优化

1. 响应压缩
   - 启用 gzip 压缩
   - 大响应数据分页

2. 缓存策略
   - 合理使用 HTTP 缓存头
   - 实现数据缓存

3. 限流措施
   - API 调用频率限制
   - 并发请求限制