import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'ant-design-vue/es'
import { useUserStore } from '@/store/user'

export interface ResponseData<T = any> {
  code: number
  data: T
  message: string
}

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 5000
})

service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    message.error('请求发送失败')
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse<ResponseData<any>>) => {
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

const request = <T = any>(config: AxiosRequestConfig): Promise<ResponseData<T>> => {
  return service(config)
}

export default request