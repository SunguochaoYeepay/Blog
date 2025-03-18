import { beforeAll, afterAll, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { http } from 'msw';

// 创建 MSW 服务器实例
export const server = setupServer();

// 全局测试设置
beforeAll(() => {
  // 启动 MSW 服务器
  server.listen({ onUnhandledRequest: 'error' });
});

afterAll(() => {
  // 关闭 MSW 服务器
  server.close();
});

afterEach(() => {
  // 每个测试后重置处理程序
  server.resetHandlers();
});