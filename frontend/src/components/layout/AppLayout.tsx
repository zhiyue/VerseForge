import React, { useState } from 'react';
import { Layout, Menu, Breadcrumb, Button, Avatar, Dropdown } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  BookOutlined,
  RobotOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

const { Header, Sider, Content } = Layout;

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  path: string;
  children?: MenuItem[];
}

const menuItems: MenuItem[] = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
    path: '/',
  },
  {
    key: 'novels',
    icon: <BookOutlined />,
    label: '小说管理',
    path: '/novels',
  },
  {
    key: 'agents',
    icon: <RobotOutlined />,
    label: 'AI智能体',
    path: '/agents',
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: '系统设置',
    path: '/settings',
  },
];

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleMenuClick = (path: string) => {
    navigate(path);
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
      onClick: () => navigate('/settings/profile'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout,
    },
  ];

  // 计算当前面包屑
  const getBreadcrumbs = () => {
    const pathSnippets = location.pathname.split('/').filter(i => i);
    const breadcrumbItems = [
      {
        title: '首页',
        path: '/',
      },
    ];

    pathSnippets.forEach((_, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      const menuItem = menuItems.find(item => item.path === url);
      if (menuItem) {
        breadcrumbItems.push({
          title: menuItem.label,
          path: url,
        });
      }
    });

    return breadcrumbItems;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className="p-4 text-white text-xl font-bold">
          {collapsed ? 'VF' : 'VerseForge'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems.map(item => ({
            key: item.path,
            icon: item.icon,
            label: item.label,
            onClick: () => handleMenuClick(item.path),
          }))}
        />
      </Sider>
      <Layout>
        <Header className="bg-white p-0 flex justify-between items-center">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="w-16 h-16"
          />
          <div className="px-4">
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div className="cursor-pointer flex items-center">
                <Avatar icon={<UserOutlined />} className="mr-2" />
                <span>{user?.username}</span>
              </div>
            </Dropdown>
          </div>
        </Header>
        <div className="bg-white p-4">
          <Breadcrumb items={getBreadcrumbs()} />
        </div>
        <Content className="m-4 p-4 bg-white">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;