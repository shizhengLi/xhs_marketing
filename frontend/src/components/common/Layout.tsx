import React, { ReactNode } from 'react';
import { Layout as AntLayout, Menu, theme } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  SearchOutlined,
  FileTextOutlined,
  BarChartOutlined,
  UserOutlined,
  LogoutOutlined,
  CloudSyncOutlined
} from '@ant-design/icons';

const { Header, Content, Sider } = AntLayout;

interface LayoutProps {
  children?: ReactNode;
}

const Layout: React.FC<LayoutProps> = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
      onClick: () => navigate('/dashboard')
    },
    {
      key: '/keywords',
      icon: <SearchOutlined />,
      label: '关键词管理',
      onClick: () => navigate('/keywords')
    },
    {
      key: '/crawler',
      icon: <CloudSyncOutlined />,
      label: '爬虫管理',
      onClick: () => navigate('/crawler')
    },
    {
      key: '/posts',
      icon: <FileTextOutlined />,
      label: '热点内容',
      onClick: () => navigate('/posts')
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: '分析报告',
      onClick: () => navigate('/reports')
    },
  ];

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        theme="dark"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{
          height: 32,
          margin: 16,
          color: 'white',
          textAlign: 'center',
          fontSize: '18px',
          fontWeight: 'bold'
        }}>
          小红书监控
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <AntLayout style={{ marginLeft: 200 }}>
        <Header style={{
          padding: '0 24px',
          background: colorBgContainer,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
            欢迎使用小红书热点监控工具
          </div>
          <Menu
            mode="horizontal"
            style={{ minWidth: 0, flex: 0, border: 'none' }}
            items={[
              {
                key: 'user',
                icon: <UserOutlined />,
                label: '个人中心',
                onClick: () => navigate('/profile')
              },
              {
                key: 'logout',
                icon: <LogoutOutlined />,
                label: '退出登录',
                onClick: handleLogout
              }
            ]}
          />
        </Header>
        <Content style={{
          margin: '24px 16px',
          padding: 24,
          minHeight: 280,
          background: colorBgContainer,
        }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;