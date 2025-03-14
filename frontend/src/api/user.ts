import request from '@/utils/request';

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
}

export interface UserQuery {
  username?: string;
  email?: string;
  role?: string;
  department?: string;
  skip?: number;
  limit?: number;
}

export interface UserCreateDTO {
  username: string;
  email: string;
  password: string;
  role: string;
  full_name: string;
  department?: string;
  avatar?: string;
}

export interface UserUpdateDTO {
  username?: string;
  email?: string;
  password?: string;
  role?: string;
  department?: string;
  avatar?: string;
  status?: string;
}

export interface ListResponse<T> {
  data: T[];
  total: number;
}

export const userApi = {
  // 获取用户列表
  getList: (params: UserQuery) => {
    return request<ListResponse<User>>({ url: '/api/users', method: 'get', params });
  },

  // 获取单个用户
  getById: (id: number) => {
    return request<User>({ url: `/api/users/${id}`, method: 'get' });
  },

  // 创建用户
  create: (data: UserCreateDTO) => {
    return request<User>({ url: '/api/users', method: 'post', data });
  },

  // 更新用户
  update: (id: number, data: UserUpdateDTO) => {
    return request<User>({ url: `/api/users/${id}`, method: 'put', data });
  },

  // 删除用户
  delete: (id: number) => {
    return request({ url: `/api/users/${id}`, method: 'delete' });
  },

  // 更新用户头像
  updateAvatar: (id: number, avatarData: string) => {
    return request({ url: `/api/users/${id}/avatar`, method: 'put', data: { avatar: avatarData } });
  },

  // 批量删除用户
  batchDelete: (ids: number[]) => {
    return request({ url: '/api/users', method: 'delete', data: { ids } });
  },

  // 修改密码
  changePassword: (id: number, oldPassword: string, newPassword: string) => {
    return request({ url: `/api/users/${id}/password`, method: 'put', data: {
      old_password: oldPassword,
      new_password: newPassword
    } });
  }
};