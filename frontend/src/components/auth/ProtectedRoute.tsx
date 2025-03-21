import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';

import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  // 如果正在加载用户信息，显示加载状态
  if (!user && isAuthenticated) {
    return (
      <div className="flex h-screen w-screen items-center justify-center">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  // 如果未登录，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果已登录，显示受保护的内容
  return <>{children}</>;
};

export default ProtectedRoute;