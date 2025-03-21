import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';

import { login as loginApi, signup as signupApi, logout as logoutApi } from '@/services/auth';
import { useMessage } from './useMessage';

export const useAuth = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useMessage();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // 获取当前用户信息
  const { data: user, refetch } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setIsAuthenticated(false);
          return null;
        }
        
        // TODO: 调用获取用户信息API
        setIsAuthenticated(true);
        return { id: 1, username: 'test' }; // 临时数据
      } catch (error) {
        setIsAuthenticated(false);
        return null;
      }
    },
    retry: false
  });

  // 登录
  const loginMutation = useMutation({
    mutationFn: loginApi,
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token);
      setIsAuthenticated(true);
      showSuccess('登录成功');
      navigate('/');
      refetch();
    },
    onError: (error: any) => {
      showError(error.message || '登录失败');
    }
  });

  // 注册
  const signupMutation = useMutation({
    mutationFn: signupApi,
    onSuccess: () => {
      showSuccess('注册成功，请登录');
      navigate('/login');
    },
    onError: (error: any) => {
      showError(error.message || '注册失败');
    }
  });

  // 登出
  const logoutMutation = useMutation({
    mutationFn: logoutApi,
    onSuccess: () => {
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      showSuccess('已退出登录');
      navigate('/login');
    },
    onError: (error: any) => {
      showError(error.message || '退出失败');
    }
  });

  // 初始化认证状态
  const initialize = useCallback(async () => {
    await refetch();
  }, [refetch]);

  const login = useCallback(
    (values: { email: string; password: string }) => {
      loginMutation.mutate(values);
    },
    [loginMutation]
  );

  const signup = useCallback(
    (values: { email: string; username: string; password: string }) => {
      signupMutation.mutate(values);
    },
    [signupMutation]
  );

  const logout = useCallback(() => {
    logoutMutation.mutate();
  }, [logoutMutation]);

  return {
    user,
    isAuthenticated,
    isLoading: loginMutation.isPending,
    initialize,
    login,
    signup,
    logout
  };
};