import request from '@/utils/request';
import type { PaginatedResponse, ApiResponse, PaginationQuery } from '@/types/common';

export interface Tag {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface TagCreate {
  name: string;
  slug?: string;
  description?: string;
}

export interface TagUpdate {
  name?: string;
  slug?: string;
  description?: string;
}

export interface TagQuery extends PaginationQuery {
  name?: string;
}

export const tagApi = {
  // 获取标签列表
  list: (params?: TagQuery): Promise<ApiResponse<PaginatedResponse<Tag>>> => {
    return request({
      url: '/api/tags',
      method: 'get',
      params
    });
  },

  // 获取所有标签（不分页）
  listAll: (): Promise<ApiResponse<Tag[]>> => {
    return request({
      url: '/api/tags/all',
      method: 'get'
    });
  },

  // 获取单个标签
  get: (id: number): Promise<ApiResponse<Tag>> => {
    return request({
      url: `/api/tags/${id}`,
      method: 'get'
    });
  },

  // 创建标签
  create: (tag: TagCreate): Promise<ApiResponse<Tag>> => {
    return request({
      url: '/api/tags',
      method: 'post',
      data: tag
    });
  },

  // 更新标签
  update: (id: number, tag: TagUpdate): Promise<ApiResponse<Tag>> => {
    return request({
      url: `/api/tags/${id}`,
      method: 'put',
      data: tag
    });
  },

  // 删除标签
  delete: (id: number): Promise<ApiResponse<void>> => {
    return request({
      url: `/api/tags/${id}`,
      method: 'delete'
    });
  }
};