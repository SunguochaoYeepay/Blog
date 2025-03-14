<template>
  <a-layout-header class="header">
    <div class="header-left">
      <menu-unfold-outlined
        v-if="collapsed"
        class="trigger"
        @click="() => (collapsed = !collapsed)"
      />
      <menu-fold-outlined
        v-else
        class="trigger"
        @click="() => (collapsed = !collapsed)"
      />
      <breadcrumb />
    </div>
    <div class="header-right">
      <a-dropdown>
        <div class="user-info">
          <a-avatar :src="userStore.userInfo?.avatar || defaultAvatar" />
          <span class="username">{{ userStore.userInfo?.username }}</span>
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="0" @click="handleProfile">
              <user-outlined />
              个人信息
            </a-menu-item>
            <a-menu-item key="1" @click="handleSettings">
              <setting-outlined />
              系统设置
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="3" @click="handleLogout">
              <logout-outlined />
              退出登录
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </a-layout-header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/store/user'
import Breadcrumb from './Breadcrumb.vue'
import defaultAvatar from '@/assets/default-avatar.png'

const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const handleProfile = () => {
  router.push('/admin/profile')
}

const handleSettings = () => {
  router.push('/admin/settings')
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    message.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    message.error('退出登录失败')
  }
}
</script>

<style lang="less" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .header-left {
    display: flex;
    align-items: center;

    .trigger {
      padding: 0 24px;
      font-size: 18px;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: #1890ff;
      }
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      padding: 0 12px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: rgba(0, 0, 0, 0.025);
      }

      .username {
        margin-left: 8px;
        color: rgba(0, 0, 0, 0.85);
      }
    }
  }
}
</style> 