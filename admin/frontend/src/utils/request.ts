import axios from 'axios'
import type { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'ant-design-vue/es'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import type { ApiResponse } from '@/types/common'

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      if (config.headers) {
        config.headers['Authorization'] = `Bearer ${userStore.token}`
      } else {
        config.headers = {
          Authorization: `Bearer ${userStore.token}`
        }
      }
    }
    
    // 如果请求已经设置了 Content-Type，不修改
    if (config.headers && config.headers['Content-Type']) {
      return config
    }
    
    // 其他请求默认使用 application/json
    config.headers = config.headers || {}
    config.headers['Content-Type'] = 'application/json'
    return config
  },
  (error: AxiosError) => {
    message.error('请求发送失败')
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    
    // 如果响应成功但业务状态码不是200，显示错误信息
    if (res.code !== 200) {
      message.error(res.message || 'Error')
      
      // 401: 未登录或token过期
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.logout().then(() => {
          router.push('/login')
        })
      }
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res
  },
  (error: AxiosError) => {
    message.error(error.message)
    return Promise.reject(error)
  }
)

// 封装 request 函数
const request = <T = any>(config: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return service(config) as Promise<ApiResponse<T>>
}

export default request