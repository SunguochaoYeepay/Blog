import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { User } from '@/api/user';

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('');
  const userInfo = ref<User | null>(null);

  function setToken(newToken: string) {
    token.value = newToken;
  }

  function setUserInfo(user: User) {
    userInfo.value = user;
  }

  async function logout() {
    token.value = '';
    userInfo.value = null;
  }

  return {
    token,
    userInfo,
    setToken,
    setUserInfo,
    logout
  };
}); 