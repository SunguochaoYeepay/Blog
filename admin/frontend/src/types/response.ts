// 分页响应类型
export interface PageResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
}

// API响应类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
} 