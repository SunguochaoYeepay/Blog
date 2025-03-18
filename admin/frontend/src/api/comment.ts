import request from '@/utils/request'
import type { CommentQuery, CommentResponse, CommentUpdate } from '@/types/comment'

/**
 * 获取评论列表
 */
export function getComments(params: CommentQuery) {
  return request<{
    items: CommentResponse[]
    total: number
    page: number
    size: number
    total_pages: number
  }>({
    url: '/api/comments',
    method: 'get',
    params
  })
}

/**
 * 获取文章评论列表
 */
export function getArticleComments(articleId: number, params: CommentQuery) {
  return request<{
    items: CommentResponse[]
    total: number
    page: number
    size: number
    total_pages: number
  }>({
    url: `/api/articles/${articleId}/comments`,
    method: 'get',
    params: { ...params, article_id: articleId }
  })
}

/**
 * 获取用户评论列表
 */
export function getUserComments(userId: number, params: CommentQuery) {
  return request<{
    items: CommentResponse[]
    total: number
    page: number
    size: number
    total_pages: number
  }>({
    url: '/api/comments',
    method: 'get',
    params: { ...params, user_id: userId }
  })
}

/**
 * 获取评论详情
 */
export function getComment(id: number) {
  return request<CommentResponse>({
    url: `/api/comments/${id}`,
    method: 'get'
  })
}

/**
 * 更新评论
 */
export function updateComment(id: number, data: CommentUpdate) {
  return request<CommentResponse>({
    url: `/api/comments/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除评论
 */
export function deleteComment(id: number) {
  return request({
    url: `/api/comments/${id}`,
    method: 'delete'
  })
}

/**
 * 审核评论
 */
export function approveComment(id: number) {
  return request<CommentResponse>({
    url: `/api/comments/${id}/approve`,
    method: 'put'
  })
}

/**
 * 标记垃圾评论
 */
export function markCommentAsSpam(id: number) {
  return request<CommentResponse>({
    url: `/api/comments/${id}/mark-spam`,
    method: 'put'
  })
}