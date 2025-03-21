import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';

import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import LoginPage from '@/pages/auth/LoginPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import NovelsPage from '@/pages/novels/NovelsPage';
import NovelDetailPage from '@/pages/novels/NovelDetailPage';
import AgentsPage from '@/pages/agents/AgentsPage';
import AgentDetailPage from '@/pages/agents/AgentDetailPage';
import AgentConfigPage from '@/pages/agents/AgentConfigPage';
import SettingsPage from '@/pages/settings/SettingsPage';

import { useAuth } from '@/hooks/useAuth';
import { useMessage } from '@/hooks/useMessage';

const AppContent = () => {
  const { isAuthenticated, initialize } = useAuth();
  const { messageApi } = useMessage();

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          
          {/* 小说相关路由 */}
          <Route path="novels">
            <Route index element={<NovelsPage />} />
            <Route path=":novelId" element={<NovelDetailPage />} />
          </Route>
          
          {/* Agent相关路由 */}
          <Route path="agents">
            <Route index element={<AgentsPage />} />
            <Route path=":agentId" element={<AgentDetailPage />} />
            <Route path=":agentId/config" element={<AgentConfigPage />} />
          </Route>
          
          {/* 设置页面 */}
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
      
      {messageApi}
    </Router>
  );
};

const App = () => {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1677ff',
        },
      }}
    >
      <AntdApp>
        <AppContent />
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;