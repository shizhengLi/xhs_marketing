import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000, // 增加到30秒
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          message.error('未授权，请重新登录');
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          message.error('拒绝访问');
          break;
        case 404:
          message.error('请求地址不存在');
          break;
        case 500:
          message.error('服务器错误');
          break;
        default:
          message.error(error.response.data?.detail || '请求失败');
      }
    } else {
      message.error('网络错误');
    }
    return Promise.reject(error);
  }
);

export default request;