## 评论管理

### 评论批量操作

支持对评论进行批量操作，包括：

1. 批量审核通过评论
```http
POST /api/comments/batch-approve
Content-Type: application/json

{
  "comment_ids": [1, 2, 3]
}
```

2. 批量标记垃圾评论
```http
POST /api/comments/batch-spam
Content-Type: application/json

{
  "comment_ids": [1, 2, 3]
}
```

响应格式：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": 1,
      "content": "评论内容",
      "is_approved": true,
      "is_spam": false,
      "user_name": "用户名",
      "article_title": "文章标题",
      "reply_count": 0
    }
  ]
}
``` 