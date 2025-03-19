import request from '@/utils/request';
import type { ApiResponse, PaginatedResponse } from '@/types/api';
import type { ArticleCreate, ArticleResponse, ArticleQuery, Category, Tag } from './article.d';

export { ArticleCreate, ArticleResponse, ArticleQuery, Category, Tag };

export const articleApi = {
  create: (article: ArticleCreate): Promise<ApiResponse<ArticleResponse>> => 
    request({
      url: '/api/articles',
      method: 'post',
      data: article
    }),
  
  list: (params: ArticleQuery): Promise<ApiResponse<PaginatedResponse<ArticleResponse>>> => {
    return request({
      url: '/api/articles',
      method: 'get',
      params
    });
  },
  
  get: (id: number): Promise<ApiResponse<ArticleResponse>> =>
    request({
      url: `/api/articles/${id}`,
      method: 'get'
    }),
  
  update: (id: number, article: Partial<ArticleCreate>): Promise<ApiResponse<ArticleResponse>> =>
    request({
      url: `/api/articles/${id}`,
      method: 'put',
      data: article
    }),
  
  delete: (id: number): Promise<ApiResponse<void>> =>
    request({
      url: `/api/articles/${id}`,
      method: 'delete'
    }),
  
  getCategories: (): Promise<ApiResponse<Category[]>> =>
    request({
      url: '/api/categories',
      method: 'get'
    }),
  
  getTags: (): Promise<ApiResponse<Tag[]>> =>
    request({
      url: '/api/tags',
      method: 'get'
    }),
    
  uploadImage: (formData: FormData): Promise<ApiResponse<{ url: string }>> =>
    request({
      url: '/api/upload/image',
      method: 'post',
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      data: formData
    })
}; 