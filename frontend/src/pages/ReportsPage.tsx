import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  message,
  Space,
  Row,
  Col,
  Statistic,
  Typography,
  Divider,
  Alert,
  Tabs,
  Spin,
  Tag,
  Progress,
  Timeline,
  Collapse
} from 'antd';
import {
  FireOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  TrophyOutlined,
  EyeOutlined,
  LineChartOutlined,
  FileTextOutlined,
  RocketOutlined,
  StarOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface KeywordAnalysis {
  keyword: string;
  keyword_id: number;
  posts_analyzed: number;
  analysis: any;
  analysis_date: string;
  model_used: string;
}

const REPORTS_STORAGE_KEY = 'xhs_reports_data';

const ReportsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [keywordAnalyses, setKeywordAnalyses] = useState<KeywordAnalysis[]>([]);
  const [comprehensiveReport, setComprehensiveReport] = useState<string>('');
  const [activeTab, setActiveTab] = useState('keywords');

  // 从localStorage加载保存的数据
  useEffect(() => {
    loadSavedReports();
  }, []);

  // 当分析结果更新时保存到localStorage
  useEffect(() => {
    if (keywordAnalyses.length > 0 || comprehensiveReport) {
      saveReportsToStorage();
    }
  }, [keywordAnalyses, comprehensiveReport]);

  // 保存报告数据到localStorage
  const saveReportsToStorage = () => {
    try {
      const reportsData = {
        keywordAnalyses,
        comprehensiveReport,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem(REPORTS_STORAGE_KEY, JSON.stringify(reportsData));
    } catch (error) {
      console.error('保存报告数据失败:', error);
    }
  };

  // 从localStorage加载保存的报告数据
  const loadSavedReports = () => {
    try {
      const savedData = localStorage.getItem(REPORTS_STORAGE_KEY);
      if (savedData) {
        const reportsData = JSON.parse(savedData);
        if (reportsData.keywordAnalyses && reportsData.keywordAnalyses.length > 0) {
          setKeywordAnalyses(reportsData.keywordAnalyses);
          message.info(`已加载 ${reportsData.keywordAnalyses.length} 个关键词的分析结果`);
        }
        if (reportsData.comprehensiveReport) {
          setComprehensiveReport(reportsData.comprehensiveReport);
        }
      }
    } catch (error) {
      console.error('加载保存的报告数据失败:', error);
    }
  };

  // 分析各关键词热点内容
  const handleAnalyzeKeywords = async () => {
    setAnalyzing(true);
    setProgress(0);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/api/v1/reports/analyze-keywords', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setKeywordAnalyses(response.data.analyses);
        message.success(`成功分析 ${response.data.analyzed_keywords} 个关键词的热点内容`);
        setProgress(100);

        // 自动保存到localStorage
        saveReportsToStorage();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '分析失败');
    } finally {
      setAnalyzing(false);
    }
  };

  // 清除缓存的数据
  const handleClearCache = () => {
    try {
      localStorage.removeItem(REPORTS_STORAGE_KEY);
      setKeywordAnalyses([]);
      setComprehensiveReport('');
      message.success('已清除缓存的报告数据');
    } catch (error) {
      message.error('清除缓存失败');
    }
  };

  // 生成综合报告
  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/api/v1/reports/generate-comprehensive-report', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        message.success('综合热点分析报告生成成功');
        setActiveTab('report');
        // 加载报告内容
        await loadReportContent(response.data.report_id);

        // 自动保存到localStorage
        saveReportsToStorage();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '报告生成失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载报告内容
  const loadReportContent = async (reportId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/v1/reports/${reportId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setComprehensiveReport(response.data.report.content);
      }
    } catch (error: any) {
      message.error('加载报告内容失败');
    }
  };

  // 渲染关键词分析结果
  const renderKeywordAnalysis = (analysis: KeywordAnalysis) => {
    const data = analysis.analysis;

    return (
      <Card
        key={analysis.keyword_id}
        title={
          <Space>
            <Tag color="blue" style={{ fontSize: '16px' }}>
              {analysis.keyword}
            </Tag>
            <Text type="secondary">
              分析了 {analysis.posts_analyzed} 条内容
            </Text>
          </Space>
        }
        extra={
          <Tag color="green">{analysis.model_used}</Tag>
        }
        style={{ marginBottom: 16 }}
      >
        {/* 趋势亮点 */}
        {data.trend_highlights && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <FireOutlined /> 热点趋势
            </Title>
            <ul>
              {data.trend_highlights.map((trend: string, idx: number) => (
                <li key={idx}>{trend}</li>
              ))}
            </ul>
          </div>
        )}

        {/* 用户画像 */}
        {data.user_persona && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <EyeOutlined /> 用户画像
            </Title>
            <Paragraph>{data.user_persona.target_audience}</Paragraph>
            <div>
              <Text strong>痛点：</Text>
              <ul>
                {data.user_persona.pain_points?.map((point: string, idx: number) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* 成功模式 */}
        {data.content_success_patterns && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <BulbOutlined /> 内容成功模式
            </Title>
            <div>
              <Text strong>标题模式：</Text>
              <ul>
                {data.content_success_patterns.title_patterns?.map((pattern: string, idx: number) => (
                  <li key={idx}>{pattern}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* 商业机会 */}
        {data.commercial_opportunities && data.commercial_opportunities.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <RocketOutlined /> 商业机会
            </Title>
            {data.commercial_opportunities.map((opp: any, idx: number) => (
              <Card key={idx} size="small" style={{ marginBottom: 8 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>{opp.opportunity}</Text>
                  <div>
                    <Tag color={opp.feasibility === 'high' ? 'green' : opp.feasibility === 'medium' ? 'orange' : 'red'}>
                      可行性: {opp.feasibility}
                    </Tag>
                    <Text type="secondary">{opp.estimated_value}</Text>
                  </div>
                </Space>
              </Card>
            ))}
          </div>
        )}

        {/* 战略建议 */}
        {data.actionable_recommendations && (
          <div>
            <Title level={5}>
              <ThunderboltOutlined /> 行动建议
            </Title>
            <Timeline>
              {data.actionable_recommendations.map((rec: string, idx: number) => (
                <Timeline.Item key={idx}>{rec}</Timeline.Item>
              ))}
            </Timeline>
          </div>
        )}
      </Card>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <BarChartOutlined />
            <span>AI热点分析报告</span>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="primary"
              icon={<FileTextOutlined />}
              onClick={handleAnalyzeKeywords}
              loading={analyzing}
            >
              分析热点内容
            </Button>
            <Button
              icon={<LineChartOutlined />}
              onClick={handleGenerateReport}
              loading={loading}
              disabled={keywordAnalyses.length === 0}
            >
              生成综合报告
            </Button>
            <Button
              danger
              onClick={handleClearCache}
              disabled={keywordAnalyses.length === 0 && !comprehensiveReport}
            >
              清除缓存
            </Button>
          </Space>
        }
      >
        <Alert
          message="智能热点分析系统"
          description={
            <div>
              <p>利用GPT对小红书热点内容进行深度分析，按不同关键词领域提供趋势洞察、用户画像、商业机会和创作建议。</p>
              {keywordAnalyses.length > 0 && (
                <p style={{ color: '#52c41a', fontWeight: 500 }}>
                  ✅ 已缓存 {keywordAnalyses.length} 个关键词的分析结果，切换页面不会丢失数据
                </p>
              )}
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        {/* 分析进度 */}
        {analyzing && (
          <Card style={{ marginBottom: 24 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>正在进行AI热点分析...</Text>
              <Progress percent={progress} status="active" />
              <Text type="secondary">这可能需要几分钟时间，请耐心等待</Text>
            </Space>
          </Card>
        )}

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'keywords',
              label: `按关键词分析 (${keywordAnalyses.length})`,
              children: (
                <div>
                  {keywordAnalyses.length === 0 ? (
                    <Card>
                      <div style={{ textAlign: 'center', padding: '40px' }}>
                        <FireOutlined style={{ fontSize: '48px', color: '#ccc', marginBottom: 16 }} />
                        <Paragraph type="secondary">
                          还没有分析数据，请点击"分析热点内容"开始AI智能分析
                        </Paragraph>
                      </div>
                    </Card>
                  ) : (
                    <Row gutter={[16, 16]}>
                      {keywordAnalyses.map(analysis => (
                        <Col span={24} key={analysis.keyword_id}>
                          {renderKeywordAnalysis(analysis)}
                        </Col>
                      ))}
                    </Row>
                  )}
                </div>
              )
            },
            {
              key: 'report',
              label: '综合分析报告',
              children: (
                <div>
                  {!comprehensiveReport ? (
                    <Card>
                      <div style={{ textAlign: 'center', padding: '40px' }}>
                        <FileTextOutlined style={{ fontSize: '48px', color: '#ccc', marginBottom: 16 }} />
                        <Paragraph type="secondary">
                          请先分析关键词内容，然后点击"生成综合报告"
                        </Paragraph>
                      </div>
                    </Card>
                  ) : (
                    <Card>
                      <div
                        dangerouslySetInnerHTML={{ __html: comprehensiveReport.replace(/\n/g, '<br/>') }}
                        style={{
                          lineHeight: '1.8',
                          fontSize: '14px',
                          whiteSpace: 'pre-wrap'
                        }}
                      />
                    </Card>
                  )}
                </div>
              )
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default ReportsPage;