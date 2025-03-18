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

  export interface ArticleResponse extends ArticleCreate {
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
  }

  export interface ArticleQuery {
    skip?: number;
    limit?: number;
    title?: string;
    status?: 'draft' | 'published' | 'archived';
    is_featured?: boolean;
    author_id?: number;
    sort_field?: string;
    sort_order?: 'ascend' | 'descend';
  }

  export interface ArticleListResponse {
    data: ArticleResponse[];
    total: number;
  }

  export const articleApi: {
    create: (article: ArticleCreate) => Promise<{ data: ArticleResponse }>;
    list: (params: ArticleQuery) => Promise<ArticleListResponse>;
    get: (id: number) => Promise<{ data: ArticleResponse }>;
    update: (id: number, article: Partial<ArticleCreate>) => Promise<{ data: ArticleResponse }>;
    delete: (id: number) => Promise<void>;
    getCategories: () => Promise<{ data: any[] }>;
    getTags: () => Promise<{ data: any[] }>;
  };
} 