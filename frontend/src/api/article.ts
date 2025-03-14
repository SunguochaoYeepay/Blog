import request from '@/utils/request';
import type { AxiosResponse } from 'axios';

export interface ArticleCreate {
  title: string;
  slug: string;
  content: string;
  summary: string;
  meta_title?: string;
  meta_description?: string;
  keywords?: string;
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  allow_comments: boolean;
  category_ids: number[];
  tag_ids: number[];
}

export interface ArticleResponse extends Omit<ArticleCreate, 'category_ids' | 'tag_ids'> {
  id: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
  view_count: number;
  comment_count: number;
  like_count: number;
  author: {
    id: number;
    username: string;
    email: string;
  };
  categories: Category[];
  tags: Tag[];
}

export interface ArticleQuery {
  skip?: number;
  limit?: number;
  title?: string;
  status?: 'draft' | 'published' | 'archived';
  is_featured?: boolean;
  author_id?: number;
  sort_field?: string;
  sort_order?: 'ascend' | 'descend';
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export const articleApi = {
  create: (article: ArticleCreate): Promise<ApiResponse<ArticleResponse>> => 
    request({
      url: '/api/articles',
      method: 'post',
      data: article
    }),
  
  list: (params: ArticleQuery): Promise<ApiResponse<{ data: ArticleResponse[]; total: number }>> => {
    return request({
      url: '/api/articles',
      method: 'get',
      params: {
        ...params,
        keyword: params.title, // 后端使用 keyword 作为标题搜索参数
      }
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
    })
}; 