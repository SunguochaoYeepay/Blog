import { defineStore } from 'pinia';
import { ref } from 'vue';
import { authApi } from '@/api/auth';
import type { User } from '@/api/user';
import type { LoginData } from '@/api/auth';

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '');
  const userInfo = ref<User | null>(null);

  // 登录
  const login = async (loginData: LoginData) => {
    const response = await authApi.login(loginData);
    const { access_token } = response.data;
    token.value = access_token;
    localStorage.setItem('token', access_token);
    await getUserInfo(); // 登录后获取用户信息
  };

  // 登出
  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      // 无论退出是否成功，都清除本地状态
      token.value = '';
      userInfo.value = null;
      localStorage.removeItem('token');
    }
  };

  // 获取用户信息
  const getUserInfo = async () => {
    if (!token.value) return;
    try {
      const response = await authApi.getCurrentUser();
      userInfo.value = response.data;
    } catch (error) {
      console.error('Failed to get user info:', error);
      // 如果获取用户信息失败，可能是token过期，清除登录状态
      token.value = '';
      userInfo.value = null;
      localStorage.removeItem('token');
    }
  };

  return {
    token,
    userInfo,
    login,
    logout,
    getUserInfo,
  };
}); 