import { apiClient } from './apiClient';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

/**
 * 用户登录
 */
export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>('/auth/login', {
    username: data.email, // API使用username字段作为邮箱
    password: data.password,
  });
  return response.data;
};

/**
 * 用户注册
 */
export const signup = async (data: SignupRequest): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/auth/signup', data);
  return response.data;
};

/**
 * 退出登录
 */
export const logout = async (): Promise<void> => {
  await apiClient.post('/auth/logout');
};

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<UserResponse>('/users/me');
  return response.data;
};

/**
 * 重置密码
 */
export const resetPassword = async (newPassword: string): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/auth/reset-password', {
    new_password: newPassword,
  });
  return response.data;
};