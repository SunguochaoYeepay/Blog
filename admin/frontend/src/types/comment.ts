// 评论状态类型
export type CommentStatus = 'all' | 'pending' | 'approved' | 'spam'

// 评论状态选项
export const COMMENT_STATUS_OPTIONS = [
  { label: '全部', value: 'all' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '垃圾评论', value: 'spam' }
] as const

// 评论响应类型
export interface CommentResponse {
  id: number
  content: string
  article_id: number
  article_title?: string
  user_id: number
  user_name?: string
  parent_id?: number
  is_approved: boolean
  is_spam: boolean
  ip_address?: string
  user_agent?: string
  created_at: string
  updated_at?: string
  like_count: number
}

// 评论查询参数类型
export interface CommentQuery {
  keyword?: string
  status?: CommentStatus
  article_id?: number
  article_title?: string
  user_id?: number
  start_date?: string
  end_date?: string
  page?: number
  size?: number
}

// 评论更新类型
export interface CommentUpdate {
  content?: string
  is_approved?: boolean
  is_spam?: boolean
}