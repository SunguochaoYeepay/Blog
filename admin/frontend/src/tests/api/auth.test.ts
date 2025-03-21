import { describe, it, expect, beforeEach } from 'vitest';
import { http } from 'msw';
import { server } from '../setup';
import { login, register } from '@/api/auth';

describe('Auth API', () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  describe('login', () => {
    const loginData = {
      username: 'testuser',
      password: 'testpassword'
    };

    const mockLoginResponse = {
      code: 200,
      message: '登录成功',
      data: {
        access_token: 'mock-token',
        token_type: 'bearer'
      }
    };

    beforeEach(() => {
      // 设置登录接口的模拟响应
      server.use(
        http.post(`${baseUrl}/api/auth/login`, async ({ request }) => {
          const body = await request.json();
          if (body.username === loginData.username && body.password === loginData.password) {
            return new Response(JSON.stringify(mockLoginResponse), {
              headers: { 'Content-Type': 'application/json' }
            });
          }
          return new Response(
            JSON.stringify({
              code: 401,
              message: '用户名或密码错误'
            }),
            {
              status: 401,
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
      );
    });

    it('should login successfully with correct credentials', async () => {
      const response = await login(loginData);
      expect(response.code).toBe(200);
      expect(response.message).toBe('登录成功');
      expect(response.data.access_token).toBe('mock-token');
    });

    it('should fail with incorrect credentials', async () => {
      try {
        await login({ username: 'wrong', password: 'wrong' });
      } catch (error: any) {
        expect(error.response.status).toBe(401);
        expect(error.response.data.message).toBe('用户名或密码错误');
      }
    });
  });

  describe('register', () => {
    const registerData = {
      username: 'newuser',
      email: 'newuser@example.com',
      password: 'newpassword',
      full_name: 'New User',
      department: 'IT',
      role: 'user'
    };

    const mockRegisterResponse = {
      code: 201,
      message: '注册成功',
      data: {
        access_token: 'mock-token',
        token_type: 'bearer'
      }
    };

    beforeEach(() => {
      // 设置注册接口的模拟响应
      server.use(
        http.post(`${baseUrl}/api/auth/register`, async ({ request }) => {
          const body = await request.json();
          if (body.username === registerData.username) {
            return new Response(JSON.stringify(mockRegisterResponse), {
              status: 201,
              headers: { 'Content-Type': 'application/json' }
            });
          }
          return new Response(
            JSON.stringify({
              code: 400,
              message: '用户名已存在'
            }),
            {
              status: 400,
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
      );
    });

    it('should register successfully with valid data', async () => {
      const response = await register(registerData);
      expect(response.code).toBe(201);
      expect(response.message).toBe('注册成功');
      expect(response.data.access_token).toBe('mock-token');
    });

    it('should fail with existing username', async () => {
      try {
        await register({
          ...registerData,
          username: 'existinguser'
        });
      } catch (error: any) {
        expect(error.response.status).toBe(400);
        expect(error.response.data.message).toBe('用户名已存在');
      }
    });
  });
});