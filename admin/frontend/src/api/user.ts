import request from '@/utils/request';
import type { PaginatedResponse, ApiResponse, PaginationQuery } from '@/types/common';

export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'editor' | 'user';
  department?: string;
  phone?: string;
  bio?: string;
  full_name: string;
  status: 'active' | 'inactive';
  last_login?: string;
  created_at: string;
  updated_at: string;
  articles_count?: number;
  comments_count?: number;
}

export interface UserQuery extends PaginationQuery {
  username?: string;
  email?: string;
  role?: string;
  department?: string;
}

export interface UserCreateDTO {
  username: string;
  email: string;
  password: string;
  full_name: string;
  department?: string;
  role?: string;
  avatar?: string;
  phone?: string;
  bio?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdateDTO {
  username?: string;
  email?: string;
  password?: string;
  full_name?: string;
  department?: string;
  role?: string;
  avatar?: string;
  phone?: string;
  bio?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface ListResponse<T> {
  data: T[];
  total: number;
}

export default {
  // 获取用户列表
  list: (params: UserQuery): Promise<ApiResponse<PaginatedResponse<User>>> => {
    return request({
      url: '/api/users',
      method: 'get',
      params,
    });
  },

  // 获取单个用户
  getById: (id: number): Promise<ApiResponse<User>> => {
    return request({
      url: `/api/users/${id}`,
      method: 'get'
    });
  },

  // 创建用户
  create: (data: UserCreateDTO): Promise<ApiResponse<User>> => {
    return request({
      url: '/api/users',
      method: 'post',
      data
    });
  },

  // 更新用户
  update: (id: number, data: UserUpdateDTO): Promise<ApiResponse<User>> => {
    return request({
      url: `/api/users/${id}`,
      method: 'put',
      data
    });
  },

  // 删除用户
  delete: (id: number): Promise<ApiResponse<void>> => {
    return request({
      url: `/api/users/${id}`,
      method: 'delete'
    });
  },

  // 更新用户头像
  updateAvatar: async (userId: number, file: File): Promise<ApiResponse<User>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return request({
      url: `/api/users/${userId}/avatar`,
      method: 'PUT',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  // 批量删除用户
  batchDelete: (ids: number[]): Promise<ApiResponse<void>> => {
    return request({
      url: '/api/users',
      method: 'delete',
      data: { ids }
    });
  },

  // 修改密码
  changePassword: (id: number, oldPassword: string, newPassword: string): Promise<ApiResponse<void>> => {
    return request({
      url: `/api/users/${id}/password`,
      method: 'put',
      data: {
        old_password: oldPassword,
        new_password: newPassword
      }
    });
  }
};