import request from '@/utils/request';
import type { AxiosResponse } from 'axios';

export interface LoginData {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
}

export const authApi = {
  login: (data: LoginData): Promise<{ data: LoginResponse }> => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    return request({
      url: '/api/auth/login',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  },
  
  logout: (): Promise<{ data: void }> => {
    return request({
      url: '/api/auth/logout',
      method: 'post'
    });
  },

  getCurrentUser: (): Promise<{ data: UserInfo }> => {
    return request({
      url: '/api/auth/me',
      method: 'get'
    });
  }
};