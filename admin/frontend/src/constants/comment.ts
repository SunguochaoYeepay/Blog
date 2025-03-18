// 评论状态类型
export type CommentStatus = 'all' | 'pending' | 'approved' | 'spam'

// 评论状态选项
export const COMMENT_STATUS_OPTIONS = [
  { label: '全部', value: 'all' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '垃圾评论', value: 'spam' }
] as const 