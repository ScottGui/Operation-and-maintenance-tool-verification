/**
 * 认证相关 API
 */
import request from './request';

export const authApi = {
  // 登录
  login: (data) => request.post('/auth/login', data),
  
  // 登出
  logout: () => request.post('/auth/logout'),
  
  // 获取当前用户信息
  getCurrentUser: () => request.get('/auth/me'),
};
