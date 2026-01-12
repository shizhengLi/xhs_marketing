import React from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  BarChartOutlined,
  TrophyOutlined
} from '@ant-design/icons';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
  return (
    <div>
      <Title level={2}>仪表盘</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="监控关键词"
              value={0}
              prefix={<SearchOutlined />}
              styles={{ content: { color: '#3f8600' } }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="抓取内容"
              value={0}
              prefix={<FileTextOutlined />}
              styles={{ content: { color: '#cf1322' } }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="分析报告"
              value={0}
              prefix={<BarChartOutlined />}
              styles={{ content: { color: '#1890ff' } }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="热点发现"
              value={0}
              prefix={<TrophyOutlined />}
              styles={{ content: { color: '#faad14' } }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="欢迎使用小红书热点监控工具">
        <p>这是一个AI驱动的热点内容发现与分析工具，帮助你：</p>
        <ul>
          <li>🔍 智能关键词管理和扩展</li>
          <li>📈 自动抓取小红书热点内容</li>
          <li>🤖 AI内容分析和趋势预测</li>
          <li>📊 自动生成分析报告</li>
        </ul>
        <p>请从左侧菜单选择功能开始使用！</p>
      </Card>
    </div>
  );
};

export default DashboardPage;