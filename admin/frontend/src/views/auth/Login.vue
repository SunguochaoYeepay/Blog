<template>
  <div class="login-container">
    <div class="login-content">
      <h1 class="login-title">博客管理系统</h1>
      <a-form
        :model="loginForm"
        :rules="rules"
        @finish="handleSubmit"
        layout="vertical"
        autocomplete="off"
        class="login-form"
      >
        <a-form-item name="username">
          <a-input
            v-model:value="loginForm.username"
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item name="password">
          <a-input-password
            v-model:value="loginForm.password"
            placeholder="请输入密码"
            size="large"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue/es'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import type { Rule } from 'ant-design-vue/es/form'
import type { LoginParams } from '@/types/auth'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)

const loginForm = reactive<LoginParams>({
  username: '',
  password: ''
})

const rules: Record<string, Rule[]> = {
  username: [
    { required: true, message: '请输入用户名' }
  ],
  password: [
    { required: true, message: '请输入密码' }
  ]
}

const handleSubmit = async () => {
  loading.value = true
  try {
    console.log('Attempting login...')
    await userStore.login(loginForm)
    console.log('Login successful')
    message.success('登录成功')
    
    // 获取重定向地址，支持 redirect 和 redirects 两种参数名
    const redirect = (route.query.redirect || route.query.redirects) as string
    console.log('Redirect path:', redirect)
    
    // 修改重定向逻辑，处理 /admin 路径的情况
    let targetPath = '/admin/article'
    if (redirect) {
      targetPath = redirect === '/admin' ? '/admin/article' : redirect
      // 确保重定向路径以 /admin 开头
      if (!targetPath.startsWith('/admin')) {
        targetPath = '/admin/article'
      }
    }
    console.log('Target path:', targetPath)
    
    // 确保用户信息已经获取成功
    if (!userStore.userInfo) {
      console.log('Fetching user info before navigation...')
      await userStore.fetchUserInfo()
    }
    
    await router.replace(targetPath)
    console.log('Navigation complete')
  } catch (error: any) {
    console.error('Login failed:', error)
    // 错误提示已经在请求拦截器中处理了
  } finally {
    loading.value = false
  }
}
</script>

<style lang="less" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1890ff 0%, #722ed1 100%);
}

.login-content {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-title {
  margin-bottom: 40px;
  color: #1890ff;
  font-size: 28px;
  text-align: center;
  font-weight: bold;
}

.login-form {
  :deep(.ant-form-item) {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(.ant-input-affix-wrapper) {
    height: 40px;
  }

  :deep(.ant-btn) {
    height: 40px;
  }
}
</style>