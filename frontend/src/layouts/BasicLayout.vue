<template>
  <a-layout class="main-layout">
    <!-- 左侧导航 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      collapsible
      theme="light"
      :width="200"
      class="sider"
    >
      <div class="logo">博客管理系统11</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        theme="light"
      >
        <a-menu-item key="/admin" @click="handleMenuClick('/admin')">
          <template #icon>
            <HomeOutlined />
          </template>
          <span>首页</span>
        </a-menu-item>

        <a-sub-menu key="article">
          <template #icon>
            <FileOutlined />
          </template>
          <template #title>文章管理</template>
          <a-menu-item key="/admin/article" @click="handleMenuClick({ name: 'ArticleList' })">
            <span>文章列表</span>
          </a-menu-item>
          <a-menu-item key="/admin/article/create" @click="handleMenuClick({ name: 'ArticleCreate' })">
            <span>创建文章</span>
          </a-menu-item>
        </a-sub-menu>

        <a-sub-menu key="user">
          <template #icon>
            <UserOutlined />
          </template>
          <template #title>用户管理</template>
          <a-menu-item key="/admin/user" @click="handleMenuClick({ name: 'UserList' })">
            <span>用户列表</span>
          </a-menu-item>
          <a-menu-item key="/admin/user/create" @click="handleMenuClick({ name: 'UserCreate' })">
            <span>创建用户</span>
          </a-menu-item>
        </a-sub-menu>

        <a-menu-item key="/admin/tag" @click="handleMenuClick({ name: 'Tag' })">
          <template #icon>
            <TagsOutlined />
          </template>
          <span>标签管理</span>
        </a-menu-item>

        <a-menu-item key="/admin/category" @click="handleMenuClick({ name: 'Category' })">
          <template #icon>
            <FolderOutlined />
          </template>
          <span>分类管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <!-- 右侧内容区 -->
    <a-layout :style="{ marginLeft: collapsed ? '80px' : '200px' }">
      <a-layout-header class="header">
        <div class="header-toolbar">
          <div class="toolbar-left">
            <a-breadcrumb>
              <a-breadcrumb-item>首页</a-breadcrumb-item>
              <a-breadcrumb-item>{{ currentPageTitle }}</a-breadcrumb-item>
            </a-breadcrumb>
          </div>
          <div class="toolbar-right">
            <a-tooltip placement="bottomLeft">
              <template #title>
                <div class="user-info-tooltip">
                  <p><strong>用户名：</strong>{{ userStore.userInfo?.username }}</p>
                  <p><strong>邮箱：</strong>{{ userStore.userInfo?.email }}</p>
                  <p><strong>角色：</strong>{{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</p>
                </div>
              </template>
              <a-avatar :size="32" class="user-avatar">
                {{ userStore.userInfo?.username.charAt(0).toUpperCase() }}
              </a-avatar>
            </a-tooltip>
            <a-dropdown>
              <a-button type="link" class="user-dropdown">
                <span class="username">{{ userStore.userInfo?.username }}</span>
                <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="profile">
                    <UserOutlined />
                    <span>个人信息</span>
                  </a-menu-item>
                  <a-menu-item key="settings">
                    <SettingOutlined />
                    <span>设置</span>
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout" @click="handleLogout">
                    <LogoutOutlined />
                    <span>退出登录</span>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </div>
      </a-layout-header>
      <a-layout-content class="content">
        <router-view></router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import {
  HomeOutlined,
  FileOutlined,
  UserOutlined,
  LogoutOutlined,
  DownOutlined,
  SettingOutlined,
  TagsOutlined,
  FolderOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue/es'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)
const selectedKeys = ref<string[]>([])

// 计算当前页面标题
const currentPageTitle = computed(() => {
  const path = route.path
  if (path.includes('/article')) {
    return '文章管理'
  } else if (path.includes('/user')) {
    return '用户管理'
  } else if (path.includes('/tag')) {
    return '标签管理'
  } else if (path.includes('/category')) {
    return '分类管理'
  }
  return '首页'
})

// 根据当前路由更新选中菜单
const updateSelectedKeys = () => {
  const path = route.path
  if (path === '/admin') {
    selectedKeys.value = ['/admin/article']
  } else {
    selectedKeys.value = [path]
  }
}

// 监听路由变化
watch(() => route.path, updateSelectedKeys, { immediate: true })

// 处理菜单点击
const handleMenuClick = (route: string | { name: string, params?: Record<string, any> }) => {
  if (typeof route === 'string') {
    router.push(route)
  } else {
    router.push(route)
  }
}

// 处理退出登录
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

<style scoped>
.main-layout {
  min-height: 100vh;
}

.sider {
  position: fixed;
  height: 100vh;
  left: 0;
  z-index: 10;
  box-shadow: 2px 0 8px 0 rgba(29, 35, 41, 0.05);
}

.logo {
  height: 64px;
  line-height: 64px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
  border-bottom: 1px solid #f0f0f0;
  overflow: hidden;
}

:deep(.ant-layout-header) {
  height: 64px;
  padding: 0;
  line-height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header {
  position: sticky;
  top: 0;
  z-index: 9;
}

.header-toolbar {
  height: 64px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  background: #1890ff;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.user-avatar:hover {
  background: #40a9ff;
}

.user-info-tooltip {
  padding: 4px;
}

.user-info-tooltip p {
  margin: 4px 0;
  white-space: nowrap;
}

.user-dropdown {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
  height: 100%;
}

.username {
  margin-right: 8px;
}

.content {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);
}

:deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 16px;
  border-radius: 4px;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
}
</style> 