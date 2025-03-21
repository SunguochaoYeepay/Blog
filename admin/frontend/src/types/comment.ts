import type { BaseResponse } from './common'

// 评论状态枚举
export enum CommentStatus {
  All = 'all',
  Pending = 'pending',
  Approved = 'approved',
  Spam = 'spam'
}

// 评论状态选项
export const COMMENT_STATUS_OPTIONS = [
  { label: '全部', value: CommentStatus.All },
  { label: '待审核', value: CommentStatus.Pending },
  { label: '已通过', value: CommentStatus.Approved },
  { label: '垃圾评论', value: CommentStatus.Spam }
]

// 评论查询参数
export interface CommentQuery {
  keyword?: string
  article_title?: string
  status?: CommentStatus
  start_date?: string
  end_date?: string
  include_replies?: boolean
  only_root?: boolean
  page?: number
  page_size?: number
  sort_field?: string
  sort_order?: 'ascend' | 'descend'
}

// 评论响应数据
export interface CommentResponse {
  id: number
  content: string
  article_id: number
  article_title: string
  user_id: number
  user_name: string
  parent_id: number | null
  is_approved: boolean
  is_spam: boolean
  reply_count: number
  like_count: number
  ip_address?: string
  user_agent?: string
  created_at: string
  updated_at: string
  replies?: CommentResponse[]
  level?: number
}

// 评论创建参数
export interface CommentCreate {
  content: string
  article_id: number
  parent_id?: number
}

// 评论更新参数
export interface CommentUpdate {
  content?: string
  is_approved?: boolean
  is_spam?: boolean
  parent_id?: number | null
}

// 评论树节点
export interface CommentTreeNode extends CommentResponse {
  children?: CommentTreeNode[]
  level: number
}

// 评论批量操作参数
export interface CommentBatchActionParams {
  comment_ids: number[]
}

// 评论统计信息
export interface CommentStats {
  total: number
  pending: number
  approved: number
  spam: number
  replies: number
}

// API 响应类型
export type CommentApiResponse = BaseResponse<CommentResponse>
export type CommentListResponse = BaseResponse<{
  items: CommentResponse[]
  total: number
}>
export type CommentTreeResponse = BaseResponse<CommentTreeNode[]>
export type CommentStatsResponse = BaseResponse<CommentStats>