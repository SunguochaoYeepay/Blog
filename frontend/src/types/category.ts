export interface Category {
  id: number
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  description?: string
}

export interface CategoryUpdate {
  name: string
  description?: string
}

export interface CategoryList {
  items: Category[]
  total: number
  page: number
  size: number
  total_pages: number
} 