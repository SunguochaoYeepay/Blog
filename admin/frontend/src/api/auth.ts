import request from '@/utils/request';
import type { ResponseData } from '@/utils/request';

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
  login: (data: LoginData): Promise<ResponseData<LoginResponse>> => {
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
  
  logout: (): Promise<ResponseData<void>> => {
    return request({
      url: '/api/auth/logout',
      method: 'post'
    });
  },

  getCurrentUser: (): Promise<ResponseData<UserInfo>> => {
    return request({
      url: '/api/auth/me',
      method: 'get'
    });
  }
};