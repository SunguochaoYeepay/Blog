import { describe, it, expect, beforeEach } from 'vitest';
import { http } from 'msw';
import { server } from '../setup';
import { createArticle, getArticles, getArticle, updateArticle, deleteArticle } from '@/api/article';

describe('Articles API', () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const mockArticle = {
    id: 1,
    title: 'Test Article',
    content: 'Test content',
    summary: 'Test summary',
    status: 'published',
    author_id: 1,
    created_at: '2024-03-17T00:00:00Z'
  };

  beforeEach(() => {
    // 模拟获取文章列表
    server.use(
      http.get(`${baseUrl}/api/articles`, () => {
        return new Response(
          JSON.stringify({
            code: 200,
            message: '查询成功',
            data: {
              total: 1,
              data: [mockArticle]
            }
          }),
          {
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );

    // 模拟获取单个文章
    server.use(
      http.get(`${baseUrl}/api/articles/1`, () => {
        return new Response(
          JSON.stringify({
            code: 200,
            message: '查询成功',
            data: mockArticle
          }),
          {
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );

    // 模拟创建文章
    server.use(
      http.post(`${baseUrl}/api/articles`, async ({ request }) => {
        const body = await request.json();
        return new Response(
          JSON.stringify({
            code: 201,
            message: '文章创建成功',
            data: { ...mockArticle, ...body }
          }),
          {
            status: 201,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );

    // 模拟更新文章
    server.use(
      http.put(`${baseUrl}/api/articles/1`, async ({ request }) => {
        const body = await request.json();
        return new Response(
          JSON.stringify({
            code: 200,
            message: '更新成功',
            data: { ...mockArticle, ...body }
          }),
          {
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );

    // 模拟删除文章
    server.use(
      http.delete(`${baseUrl}/api/articles/1`, () => {
        return new Response(
          JSON.stringify({
            code: 200,
            message: '删除成功'
          }),
          {
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );
  });

  describe('getArticles', () => {
    it('should fetch articles list successfully', async () => {
      const response = await getArticles();
      expect(response.code).toBe(200);
      expect(response.message).toBe('查询成功');
      expect(response.data.data).toHaveLength(1);
      expect(response.data.data[0]).toEqual(mockArticle);
    });
  });

  describe('getArticle', () => {
    it('should fetch single article successfully', async () => {
      const response = await getArticle(1);
      expect(response.code).toBe(200);
      expect(response.message).toBe('查询成功');
      expect(response.data).toEqual(mockArticle);
    });

    it('should handle non-existent article', async () => {
      server.use(
        http.get(`${baseUrl}/api/articles/999`, () => {
          return new Response(
            JSON.stringify({
              code: 404,
              message: '文章不存在'
            }),
            {
              status: 404,
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
      );

      try {
        await getArticle(999);
      } catch (error: any) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.message).toBe('文章不存在');
      }
    });
  });

  describe('createArticle', () => {
    const newArticle = {
      title: 'New Article',
      content: 'New content',
      summary: 'New summary',
      status: 'draft'
    };

    it('should create article successfully', async () => {
      const response = await createArticle(newArticle);
      expect(response.code).toBe(201);
      expect(response.message).toBe('文章创建成功');
      expect(response.data.title).toBe(newArticle.title);
    });
  });

  describe('updateArticle', () => {
    const updateData = {
      title: 'Updated Title',
      content: 'Updated content'
    };

    it('should update article successfully', async () => {
      const response = await updateArticle(1, updateData);
      expect(response.code).toBe(200);
      expect(response.message).toBe('更新成功');
      expect(response.data.title).toBe(updateData.title);
    });
  });

  describe('deleteArticle', () => {
    it('should delete article successfully', async () => {
      const response = await deleteArticle(1);
      expect(response.code).toBe(200);
      expect(response.message).toBe('删除成功');
    });
  });
});