// 组件 Props 类型定义
export interface HeroProps {
  title?: string
  subtitle?: string
}

export interface ProjectProps {
  title: string
  description: string
  image?: string
  link?: string
  tags?: string[]
}

export interface ContactProps {
  email?: string
  social?: {
    github?: string
    twitter?: string
    linkedin?: string
  }
} 