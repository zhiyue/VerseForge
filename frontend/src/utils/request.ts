import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
} from 'axios';
import { message } from 'antd';

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error: AxiosError) => {
    if (error.response) {
      const { status, data } = error.response;
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
          message.error('登录已过期，请重新登录');
          break;
        case 403:
          message.error('没有权限执行此操作');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器错误，请稍后重试');
          break;
        default:
          message.error((data as any)?.detail || '请求失败');
      }
    } else if (error.request) {
      message.error('网络错误，请检查网络连接');
    } else {
      message.error('请求配置错误');
    }
    return Promise.reject(error);
  }
);

// 封装GET请求
export const get = <T>(url: string, params?: any): Promise<T> => {
  return request.get(url, { params });
};

// 封装POST请求
export const post = <T>(url: string, data?: any): Promise<T> => {
  return request.post(url, data);
};

// 封装PUT请求
export const put = <T>(url: string, data?: any): Promise<T> => {
  return request.put(url, data);
};

// 封装DELETE请求
export const del = <T>(url: string): Promise<T> => {
  return request.delete(url);
};

// 封装PATCH请求
export const patch = <T>(url: string, data?: any): Promise<T> => {
  return request.patch(url, data);
};

// 导出请求实例
export default request;

// 类型定义
export interface Response<T = any> {
  code: number;
  data: T;
  message: string;
}

export interface PageParams {
  page?: number;
  size?: number;
  [key: string]: any;
}

export interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}