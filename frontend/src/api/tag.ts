import request from '@/utils/request';

export interface Tag {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface TagCreate {
  name: string;
  slug?: string;
  description?: string;
}

export interface TagUpdate {
  name?: string;
  slug?: string;
  description?: string;
}

export const tagService = {
  // 获取标签列表
  getTags: (skip: number = 0, limit: number = 10) => {
    return request({
      url: `/api/tags`,
      method: 'get',
      params: { skip, limit }
    });
  },

  // 获取单个标签
  getTag: (id: number) => {
    return request({
      url: `/api/tags/${id}`,
      method: 'get'
    });
  },

  // 创建标签
  createTag: (tag: TagCreate) => {
    return request({
      url: '/api/tags',
      method: 'post',
      data: tag
    });
  },

  // 更新标签
  updateTag: (id: number, tag: TagUpdate) => {
    return request({
      url: `/api/tags/${id}`,
      method: 'put',
      data: tag
    });
  },

  // 删除标签
  deleteTag: (id: number) => {
    return request({
      url: `/api/tags/${id}`,
      method: 'delete'
    });
  }
};