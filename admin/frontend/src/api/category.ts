import request from '@/utils/request'
import type { Category, CategoryCreate, CategoryUpdate, CategoryList } from '@/types/category'
import type { PaginatedResponse, ApiResponse, PaginationQuery } from '@/types/common'

export interface CategoryQuery extends PaginationQuery {
  name?: string;
}

export const categoryApi = {
  // 创建分类
  create: (data: CategoryCreate): Promise<ApiResponse<Category>> => {
    return request({
      url: '/api/categories',
      method: 'post',
      data
    });
  },

  // 获取分类列表
  list: (params?: CategoryQuery): Promise<ApiResponse<PaginatedResponse<Category>>> => {
    return request({
      url: '/api/categories',
      method: 'get',
      params
    });
  },

  // 获取所有分类（不分页）
  listAll: (): Promise<ApiResponse<Category[]>> => {
    return request({
      url: '/api/categories/all',
      method: 'get'
    });
  },

  // 获取单个分类
  get: (id: number): Promise<ApiResponse<Category>> => {
    return request({
      url: `/api/categories/${id}`,
      method: 'get'
    });
  },

  // 更新分类
  update: (id: number, data: CategoryUpdate): Promise<ApiResponse<Category>> => {
    return request({
      url: `/api/categories/${id}`,
      method: 'put',
      data
    });
  },

  // 删除分类
  delete: (id: number): Promise<ApiResponse<void>> => {
    return request({
      url: `/api/categories/${id}`,
      method: 'delete'
    });
  }
};

// 获取分类列表
export const getCategories = (params: CategoryQuery) => {
  return request<ApiResponse<{
    items: CategoryResponse[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }>>({
    url: '/api/categories',
    method: 'get',
    params
  })
}