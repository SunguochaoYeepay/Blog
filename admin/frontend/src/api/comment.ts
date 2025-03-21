import request from '@/utils/request'
import type { CommentQuery, CommentResponse, CommentUpdate, CommentStatus } from '@/types/comment'
import type { ApiResponse, PaginatedResponse } from '@/types/common'

// 获取评论列表
export const getComments = (params: CommentQuery): Promise<ApiResponse<PaginatedResponse<CommentResponse>>> => {
  return request({
    url: '/api/comments',
    method: 'get',
    params
  })
}

// 获取评论详情
export const getComment = (id: number): Promise<ApiResponse<CommentResponse>> => {
  return request({
    url: `/api/comments/${id}`,
    method: 'get'
  })
}

// 更新评论
export const updateComment = (id: number, data: CommentUpdate): Promise<ApiResponse<CommentResponse>> => {
  return request({
    url: `/api/comments/${id}`,
    method: 'put',
    data
  })
}

// 删除评论
export const deleteComment = (id: number): Promise<ApiResponse<null>> => {
  return request({
    url: `/api/comments/${id}`,
    method: 'delete'
  })
}

// 批量删除评论
export const batchDeleteComments = (ids: number[]): Promise<ApiResponse<null>> => {
  return request({
    url: '/api/comments',
    method: 'delete',
    data: { ids }
  })
}

// 获取评论回复列表
export const getCommentReplies = (id: number, params: CommentQuery): Promise<ApiResponse<PaginatedResponse<CommentResponse>>> => {
  return request({
    url: `/api/comments/${id}/replies`,
    method: 'get',
    params
  })
}

// 获取评论树结构
export const getCommentTree = (articleId: number, params?: CommentQuery): Promise<ApiResponse<CommentResponse[]>> => {
  return request({
    url: `/api/comments/tree/${articleId}`,
    method: 'get',
    params
  })
}

// 获取子评论列表
export const getChildComments = (parentId: number, params?: CommentQuery): Promise<ApiResponse<PaginatedResponse<CommentResponse>>> => {
  return request({
    url: `/api/comments/${parentId}/children`,
    method: 'get',
    params
  })
}

// 移动评论（更改父评论）
export const moveComment = (id: number, newParentId: number | null): Promise<ApiResponse<CommentResponse>> => {
  return request({
    url: `/api/comments/${id}/move`,
    method: 'put',
    data: { parent_id: newParentId }
  })
}

// 审核通过评论
export const approveComment = (id: number): Promise<ApiResponse<CommentResponse>> => {
  return request({
    url: `/api/comments/${id}/approve`,
    method: 'post'
  })
}

// 批量审核通过评论
export const batchApproveComments = (ids: number[]): Promise<ApiResponse<null>> => {
  return request({
    url: '/api/comments/approve',
    method: 'post',
    data: { ids }
  })
}

// 标记评论为垃圾评论
export const markCommentAsSpam = (id: number): Promise<ApiResponse<CommentResponse>> => {
  return request({
    url: `/api/comments/${id}/spam`,
    method: 'post'
  })
}

// 批量标记为垃圾评论
export const batchMarkAsSpam = (ids: number[]): Promise<ApiResponse<null>> => {
  return request({
    url: '/api/comments/spam',
    method: 'post',
    data: { ids }
  })
}

// 获取评论统计信息
export const getCommentStats = (articleId?: number): Promise<ApiResponse<{
  total: number
  pending: number
  approved: number
  spam: number
  replies: number
}>> => {
  return request({
    url: '/api/comments/stats',
    method: 'get',
    params: articleId ? { article_id: articleId } : undefined
  })
}
