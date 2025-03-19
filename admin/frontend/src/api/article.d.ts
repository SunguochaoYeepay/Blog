import type { ApiResponse } from '@/types/api';

declare module '@/api/article' {
  export interface ArticleCreate {
    title: string;
    slug: string;
    content: string;
    summary: string;
    meta_title?: string;
    meta_description?: string;
    keywords?: string;
    status: 'draft' | 'published' | 'archived';
    is_featured: boolean;
    allow_comments: boolean;
    category_ids: number[];
    tag_ids: number[];
  }

  export interface ArticleResponse extends Omit<ArticleCreate, 'category_ids' | 'tag_ids'> {
    id: number;
    created_at: string;
    updated_at: string;
    published_at?: string;
    view_count: number;
    comment_count: number;
    like_count: number;
    author: {
      id: number;
      username: string;
      email: string;
    };
    categories: Category[];
    tags: Tag[];
  }

  export interface ArticleQuery {
    page?: number;
    size?: number;
    title?: string;
    status?: 'draft' | 'published' | 'archived';
    is_featured?: boolean;
    author_id?: number;
    sort_field?: string;
    sort_order?: 'ascend' | 'descend';
  }

  export interface Category {
    id: number;
    name: string;
    slug: string;
    description?: string;
  }

  export interface Tag {
    id: number;
    name: string;
    slug: string;
  }

  export interface ArticleListResponse {
    data: ArticleResponse[];
    total: number;
  }

  export interface ArticleApi {
    create: (article: ArticleCreate) => Promise<ApiResponse<ArticleResponse>>;
    list: (params: ArticleQuery) => Promise<ApiResponse<PaginatedResponse<ArticleResponse>>>;
    get: (id: number) => Promise<ApiResponse<ArticleResponse>>;
    update: (id: number, article: Partial<ArticleCreate>) => Promise<ApiResponse<ArticleResponse>>;
    delete: (id: number) => Promise<ApiResponse<void>>;
    getCategories: () => Promise<ApiResponse<Category[]>>;
    getTags: () => Promise<ApiResponse<Tag[]>>;
    uploadImage: (formData: FormData) => Promise<ApiResponse<{ url: string }>>;
  }

  export const articleApi: ArticleApi;
} 