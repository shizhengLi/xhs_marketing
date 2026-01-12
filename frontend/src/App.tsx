import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/common/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import KeywordsPage from './pages/KeywordsPage';
import PostsPage from './pages/PostsPage';
import CrawlerPage from './pages/CrawlerPage';
import ReportsPage from './pages/ReportsPage';

const App: React.FC = () => {
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              isAuthenticated ? (
                <Layout />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          >
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="crawler" element={<CrawlerPage />} />
            <Route path="keywords" element={<KeywordsPage />} />
            <Route path="posts" element={<PostsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="profile" element={<div>个人中心页面 - 开发中</div>} />
            <Route path="" element={<Navigate to="/dashboard" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
