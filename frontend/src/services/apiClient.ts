import axios from 'axios';
import { message } from 'antd';
import { useHistory } from 'react-router-dom';

// 创建axios实例
export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    let errorMessage = '请求失败，请重试';

    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          errorMessage = data.detail || '请求参数错误';
          break;
        case 401:
          errorMessage = '未登录或登录已过期';
          // 清除token并跳转到登录页
          const history = useHistory();
          setTimeout(() => {
            history.push('/login');
          }, 0);
          history.push('/login');
          break;
        case 403:
          errorMessage = '没有权限执行此操作';
          break;
        case 404:
          errorMessage = '请求的资源不存在';
          break;
        case 500:
          errorMessage = '服务器错误，请稍后重试';
          break;
        default:
          errorMessage = data.detail || '未知错误';
      }
    } else if (error.request) {
      errorMessage = '无法连接到服务器';
    }

    message.error(errorMessage);
    return Promise.reject(error);
  }
);

// 类型定义
export interface ApiResponse<T = any> {
  code: number;
  data: T;
  message: string;
}

// 导出通用请求方法
export const api = {
  get: <T>(url: string, params?: any) =>
    apiClient.get<T>(url, { params }).then((res) => res.data),
    
  post: <T>(url: string, data?: any) =>
    apiClient.post<T>(url, data).then((res) => res.data),
    
  put: <T>(url: string, data?: any) =>
    apiClient.put<T>(url, data).then((res) => res.data),
    
  delete: <T>(url: string) =>
    apiClient.delete<T>(url).then((res) => res.data),
    
  patch: <T>(url: string, data?: any) =>
    apiClient.patch<T>(url, data).then((res) => res.data),
};