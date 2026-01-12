import request from '../utils/request';

export const authService = {
  /**
   * 用户注册
   */
  register: (data: { username: string; email: string; password: string }) => {
    return request.post('/v1/auth/register', data);
  },

  /**
   * 用户登录
   */
  login: (username: string, password: string) => {
    return request.post('/v1/auth/login', null, {
      params: { username, password }
    });
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: () => {
    return request.get('/v1/auth/me');
  },

  /**
   * 保存token到localStorage
   */
  saveToken: (token: string) => {
    localStorage.setItem('token', token);
  },

  /**
   * 从localStorage获取token
   */
  getToken: () => {
    return localStorage.getItem('token');
  },

  /**
   * 清除token
   */
  clearToken: () => {
    localStorage.removeItem('token');
  },

  /**
   * 检查是否已登录
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
};