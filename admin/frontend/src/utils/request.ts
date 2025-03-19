import axios from 'axios'
import type { AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'ant-design-vue/es'
import { useUserStore } from '@/store/user'
import type { ApiResponse } from '@/types/api'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})

service.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${userStore.token}`
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
  (error) => {
    message.error('请求发送失败')
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<any>>) => {
    const res = response.data
    // 2xx 状态码都是成功
    if (res.code >= 200 && res.code < 300) {
      return Promise.resolve(res)
    }
    message.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  (error) => {
    // 处理 422 错误
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail
      if (Array.isArray(detail)) {
        // FastAPI 验证错误格式
        message.error(detail[0]?.msg || '请求参数错误')
      } else {
        message.error(error.response.data?.detail?.message || error.response.data?.message || '请求参数错误')
      }
    } else {
      message.error(error.response?.data?.message || error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default service