export interface Author {
  id: number
  name: string
  avatar: string
  bio: string
}

export interface BlogPost {
  id: number
  title: string
  content: string
  coverImage: string
  category: string
  date: string
  author: Author
  tags?: string[]
}

export interface BlogListResponse {
  posts: BlogPost[]
  total: number
  page: number
  pageSize: number
} 