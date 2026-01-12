import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Form,
  InputNumber,
  Select,
  message,
  Tag,
  Space,
  Tooltip,
  Modal,
  Descriptions,
  Row,
  Col,
  Statistic,
  Alert,
  Tabs,
  Typography,
  Progress,
  Divider,
  List,
  Spin,
  Radio
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  PlusOutlined,
  DeleteOutlined,
  ClockCircleOutlined,
  SyncOutlined,
  SettingOutlined,
  QrcodeOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloudSyncOutlined,
  LikeOutlined,
  StarOutlined,
  MessageOutlined,
  FireOutlined
} from '@ant-design/icons';
import { schedulerService, crawlerService, mediacrawlerService } from '../services/crawler';
import { keywordService } from '../services/keyword';

interface Keyword {
  id: number;
  keyword: string;
  group_name: string;
  is_active: boolean;
}

interface Job {
  id: string;
  name: string;
  next_run_time: string;
  trigger: string;
}

interface SchedulerStatus {
  is_running: boolean;
  jobs: Job[];
  current_time: string;
}

const CrawlerPage: React.FC = () => {
  const [form] = Form.useForm();
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [setupLoading, setSetupLoading] = useState(false);
  const [loginStatus, setLoginStatus] = useState<'unknown' | 'logged_in' | 'logged_out'>('unknown');
  const [activeTab, setActiveTab] = useState('schedule');
  const [phoneLoginForm] = Form.useForm();
  const [cookieLoginForm] = Form.useForm();
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [crawlCount, setCrawlCount] = useState<number>(15);
  const [dataImportLoading, setDataImportLoading] = useState(false);
  const [dataSummary, setDataSummary] = useState<any>(null);
  const [crawlStatistics, setCrawlStatistics] = useState<any>(null);
  const [statisticsLoading, setStatisticsLoading] = useState(false);

  // 删除数据相关状态
  const [selectedKeywordForDelete, setSelectedKeywordForDelete] = useState<string>('');
  const [deleteType, setDeleteType] = useState<string>('all');
  const [deleteLoading, setDeleteLoading] = useState(false);

  // 爬取完成状态
  const [crawlCompleted, setCrawlCompleted] = useState(false);
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlStartTime, setCrawlStartTime] = useState<Date | null>(null);
  const [lastCheckTime, setLastCheckTime] = useState<Date | null>(null);

  // 加载关键词列表
  const loadKeywords = async () => {
    try {
      const data = await keywordService.getKeywords();
      setKeywords(data);
    } catch (error) {
      message.error('加载关键词列表失败');
    }
  };

  // 加载调度器状态
  const loadSchedulerStatus = async () => {
    try {
      const data = await schedulerService.getStatus();
      setSchedulerStatus(data);
    } catch (error) {
      message.error('加载调度器状态失败');
    }
  };

  // 启动调度器
  const handleStart = async () => {
    setLoading(true);
    try {
      await schedulerService.start();
      message.success('调度器已启动');
      loadSchedulerStatus();
    } catch (error) {
      message.error('启动调度器失败');
    } finally {
      setLoading(false);
    }
  };

  // 停止调度器
  const handleStop = async () => {
    setLoading(true);
    try {
      await schedulerService.stop();
      message.success('调度器已停止');
      loadSchedulerStatus();
    } catch (error) {
      message.error('停止调度器失败');
    } finally {
      setLoading(false);
    }
  };

  // 设置定时任务
  const handleSetupSchedule = async (values: any) => {
    setSetupLoading(true);
    try {
      await schedulerService.setupSchedule({
        hour: values.hour,
        minute: values.minute,
        keyword_id: values.keyword_id || null,
        schedule_type: values.schedule_type,
        max_results: values.max_results || 15
      });
      message.success('定时任务设置成功');
      form.resetFields();
      loadSchedulerStatus();
    } catch (error) {
      message.error('设置定时任务失败');
    } finally {
      setSetupLoading(false);
    }
  };

  // 删除任务
  const handleDeleteJob = async (jobId: string) => {
    try {
      await schedulerService.deleteJob(jobId);
      message.success('任务已删除');
      loadSchedulerStatus();
    } catch (error) {
      message.error('删除任务失败');
    }
  };

  // MediaCrawler 登录相关函数
  const handleGetInstructions = async () => {
    try {
      const response = await mediacrawlerService.getInstructions();
      if (response.success) {
        // 显示登录指导信息
        console.log('登录指导:', response.instructions);
        message.info('请查看登录指导信息');
      }
    } catch (error) {
      message.error('获取登录指导失败');
    }
  };

  const handleStartMediacrawler = async () => {
    try {
      if (selectedKeywords.length === 0) {
        message.warning('请先选择要爬取的关键词');
        return;
      }

      setIsCrawling(true);
      setCrawlCompleted(false);
      setCrawlStartTime(new Date());
      setLastCheckTime(new Date());

      const response = await mediacrawlerService.startMediacrawler({
        keywords: selectedKeywords,
        count: crawlCount
      });

      if (response.success) {
        message.success(`MediaCrawler已启动，正在爬取 ${selectedKeywords.join(', ')} 的数据...`);

        // 开始检查爬取完成状态
        startCrawlCompletionCheck();
      }
    } catch (error) {
      message.error('启动MediaCrawler失败');
      setIsCrawling(false);
    }
  };

  // 检查爬取完成状态
  const startCrawlCompletionCheck = () => {
    let checkCount = 0;
    const maxChecks = 180; // 最多检查180次（30分钟）

    const checkInterval = setInterval(async () => {
      try {
        checkCount++;
        const now = new Date();
        const elapsedTime = Math.floor((now.getTime() - (crawlStartTime?.getTime() || 0)) / 1000);

        console.log(`第 ${checkCount} 次检查爬取状态，已运行 ${elapsedTime} 秒`);

        // 检查是否有新的数据文件产生
        const summary = await mediacrawlerService.getDataSummary();

        if (summary && summary.total_files > 0) {
          console.log('发现数据文件:', summary);

          // 获取今天的日期字符串
          const today = new Date();
          const todayStr = today.toISOString().split('T')[0]; // 格式: 2026-01-12

          console.log('今天日期:', todayStr);

          // 检查是否有今天创建的文件
          const hasTodayFile = summary.files?.some((file: any) => {
            const fileDate = new Date(file.modified_time);
            const fileDateStr = fileDate.toISOString().split('T')[0];
            console.log(`检查文件 ${file.name}, 日期: ${fileDateStr}`);

            // 检查文件是否是今天的，并且是在爬取开始之后创建的
            return fileDateStr === todayStr && fileDate > (crawlStartTime || new Date(0));
          });

          console.log('是否有今天的新文件:', hasTodayFile);

          if (hasTodayFile) {
            clearInterval(checkInterval);
            setCrawlCompleted(true);
            setIsCrawling(false);

            console.log('爬取完成，显示完成通知');

            // 显示完成通知
            Modal.success({
              title: '🎉 数据爬取完成！',
              content: (
                <div>
                  <p>成功爬取了 {selectedKeywords.join(', ')} 的数据</p>
                  <p>发现 {summary.total_files} 个新数据文件</p>
                  <p>请前往"数据导入"页面导入数据</p>
                </div>
              ),
              okText: '前往导入',
              onOk: () => {
                setActiveTab('import');
              }
            });

            // 刷新数据摘要
            loadDataSummary();
            return;
          }
        }

        // 如果超过最大检查次数，停止检查
        if (checkCount >= maxChecks) {
          clearInterval(checkInterval);
          console.log('达到最大检查次数，停止检查');
          setIsCrawling(false);
          message.warning('爬取检查超时，请手动检查数据文件是否已生成');
        }

        setLastCheckTime(now);
      } catch (error) {
        console.error('检查爬取状态失败:', error);
      }
    }, 10000); // 每10秒检查一次，无超时限制
  };

  const handleConfirmLogin = async (loginMethod: string) => {
    try {
      const response = await mediacrawlerService.confirmLogin(loginMethod, true);
      if (response.success) {
        message.success('登录状态已更新');
        setLoginStatus('logged_in');
      }
    } catch (error) {
      message.error('确认登录失败');
    }
  };

  const handleCheckLoginStatus = async () => {
    try {
      const status = await mediacrawlerService.getLoginStatus();
      setLoginStatus(status.is_logged_in ? 'logged_in' : 'logged_out');
      message.info(status.is_logged_in ? '已登录' : '未登录');
    } catch (error) {
      message.error('检查登录状态失败');
    }
  };

  const handleLogout = async () => {
    try {
      const response = await mediacrawlerService.resetLogin();
      if (response.success) {
        message.success('登录状态已重置');
        setLoginStatus('logged_out');
      } else {
        message.error(response.message || '重置登录状态失败');
      }
    } catch (error) {
      message.error('重置登录状态失败');
    }
  };

  const handleQuickStart = async () => {
    try {
      if (!selectedKeywords || selectedKeywords.length === 0) {
        message.warning('请选择至少一个关键词');
        return;
      }

      setIsCrawling(true);
      setCrawlCompleted(false);
      setCrawlStartTime(new Date());
      setLastCheckTime(new Date());

      message.loading({ content: '正在启动MediaCrawler...', key: 'startCrawler' });

      const response = await mediacrawlerService.quickStart(selectedKeywords, crawlCount);

      if (response.success) {
        message.success({ content: 'MediaCrawler已启动，浏览器将自动打开，请扫描二维码登录', key: 'startCrawler', duration: 5 });

        // 开始检查爬取完成状态
        startCrawlCompletionCheck();
      } else {
        message.error({ content: response.message || '启动失败', key: 'startCrawler' });
        setIsCrawling(false);
      }
    } catch (error: any) {
      console.error('启动MediaCrawler失败:', error);
      const errorMessage = error.response?.data?.detail || error.message || '未知错误';
      message.error({ content: `启动MediaCrawler失败: ${errorMessage}`, key: 'startCrawler' });
      setIsCrawling(false);
    }
  };

  const handleLoginOnly = async () => {
    try {
      message.loading({ content: '正在启动浏览器...', key: 'loginOnly' });

      const response = await mediacrawlerService.loginOnly();

      if (response.success) {
        message.success({ content: '浏览器已打开，请扫描二维码登录。登录成功后，浏览器会自动关闭。', key: 'loginOnly', duration: 5 });
      } else {
        message.error({ content: response.message || '启动失败', key: 'loginOnly' });
      }
    } catch (error: any) {
      console.error('启动浏览器失败:', error);
      const errorMessage = error.response?.data?.detail || error.message || '未知错误';
      message.error({ content: `启动浏览器失败: ${errorMessage}`, key: 'loginOnly' });
    }
  };

  // 数据导入相关函数
  const loadDataSummary = async () => {
    try {
      const summary = await mediacrawlerService.getDataSummary();
      setDataSummary(summary);
    } catch (error) {
      console.error('获取数据摘要失败:', error);
    }
  };

  const handleImportData = async (keyword: string) => {
    setDataImportLoading(true);
    try {
      const result = await mediacrawlerService.importData(keyword);

      if (result.success) {
        message.success(`数据导入成功！新增 ${result.new_saved} 条，更新 ${result.updated} 条`);
        loadDataSummary(); // 刷新数据摘要
        loadCrawlStatistics(); // 刷新统计数据
      } else {
        message.error(result.message || '导入失败');
      }
    } catch (error: any) {
      console.error('导入数据失败:', error);
      const errorMessage = error.response?.data?.detail || error.message || '未知错误';
      message.error(`导入数据失败: ${errorMessage}`);
    } finally {
      setDataImportLoading(false);
    }
  };

  // 加载统计数据
  const loadCrawlStatistics = async () => {
    setStatisticsLoading(true);
    try {
      const response = await mediacrawlerService.getCrawlStatistics();
      setCrawlStatistics(response);
    } catch (error) {
      console.error('加载统计数据失败:', error);
    } finally {
      setStatisticsLoading(false);
    }
  };

  // 删除数据
  const handleDeleteData = async () => {
    if (!selectedKeywordForDelete) {
      message.warning('请选择要删除的关键词');
      return;
    }

    // 确认删除
    Modal.confirm({
      title: '确认删除',
      content: (
        <div>
          <p>您即将删除关键词 <strong>{selectedKeywordForDelete}</strong> 的数据</p>
          <p>删除类型: <strong>{deleteType === 'all' ? '文件和数据库数据' : deleteType === 'file' ? '仅数据文件' : '仅数据库数据'}</strong></p>
          <p style={{ color: 'red', marginTop: 16 }}>⚠️ 此操作不可恢复，请确认是否继续？</p>
        </div>
      ),
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        setDeleteLoading(true);
        try {
          const result = await mediacrawlerService.deleteKeywordData(selectedKeywordForDelete, deleteType);

          if (result.success) {
            message.success(result.message || '删除成功');

            // 刷新相关数据
            loadDataSummary();
            loadCrawlStatistics();

            // 清空选择
            setSelectedKeywordForDelete('');
          } else {
            message.error(result.message || '删除失败');
          }
        } catch (error: any) {
          console.error('删除数据失败:', error);
          const errorMessage = error.response?.data?.detail || error.message || '未知错误';
          message.error(`删除数据失败: ${errorMessage}`);
        } finally {
          setDeleteLoading(false);
        }
      }
    });
  };

  useEffect(() => {
    loadKeywords();
    loadSchedulerStatus();
    handleCheckLoginStatus(); // 检查登录状态
    loadDataSummary(); // 加载数据摘要
    loadCrawlStatistics(); // 加载统计数据
    // 定时刷新状态
    const interval = setInterval(loadSchedulerStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      render: (text: string) => <code>{text}</code>
    },
    {
      title: '触发器',
      dataIndex: 'trigger',
      key: 'trigger',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '下次运行时间',
      dataIndex: 'next_run_time',
      key: 'next_run_time',
      render: (time: string) => time ? new Date(time).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: Job) => (
        <Space>
          <Tooltip title="删除任务">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteJob(record.id)}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <CloudSyncOutlined />
            <span>小红书爬虫管理</span>
          </Space>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'schedule',
              label: '定时任务管理',
              children: (
                <div>
                  <Row gutter={[16, 16]}>
                    {/* 调度器控制面板 */}
                    <Col span={24}>
                      <Card
                        title={
                          <Space>
                            <SettingOutlined />
                            <span>调度器控制</span>
                          </Space>
                        }
                        extra={
                          <Space>
                            <Button
                              type="primary"
                              icon={<PlayCircleOutlined />}
                              onClick={handleStart}
                              loading={loading}
                              disabled={schedulerStatus?.is_running}
                            >
                              启动调度器
                            </Button>
                            <Button
                              danger
                              icon={<PauseCircleOutlined />}
                              onClick={handleStop}
                              loading={loading}
                              disabled={!schedulerStatus?.is_running}
                            >
                              停止调度器
                            </Button>
                            <Button
                              icon={<SyncOutlined />}
                              onClick={loadSchedulerStatus}
                            >
                              刷新状态
                            </Button>
                          </Space>
                        }
                      >
                        <Row gutter={16}>
                          <Col span={6}>
                            <Statistic
                              title="调度器状态"
                              value={schedulerStatus?.is_running ? '运行中' : '已停止'}
                              styles={{
                                content: {
                                  color: schedulerStatus?.is_running ? '#3f8600' : '#cf1322'
                                }
                              }}
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="活跃任务数"
                              value={schedulerStatus?.jobs.length || 0}
                              suffix="个"
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="当前时间"
                              value={schedulerStatus?.current_time ?
                                new Date(schedulerStatus.current_time).toLocaleString('zh-CN') : '-'}
                              style={{ fontSize: '14px' }}
                            />
                          </Col>
                        </Row>
                      </Card>
                    </Col>

                    {/* 设置定时任务 */}
                    <Col span={24}>
                      <Card
                        title={
                          <Space>
                            <ClockCircleOutlined />
                            <span>设置定时任务</span>
                          </Space>
                        }
                      >
                        <Alert
                          title="提示"
                          description="定时任务将在指定时间自动爬取小红书热点内容。建议设置在用户活跃时段，如早上8点、中午12点、晚上8点等。"
                          type="info"
                          showIcon
                          style={{ marginBottom: 16 }}
                        />
                        <Form
                          form={form}
                          layout="inline"
                          onFinish={handleSetupSchedule}
                          initialValues={{
                            schedule_type: 'daily',
                            max_results: 15
                          }}
                        >
                          <Form.Item
                            name="schedule_type"
                            label="调度类型"
                            rules={[{ required: true }]}
                          >
                            <Select style={{ width: 120 }}>
                              <Select.Option value="daily">每日定时</Select.Option>
                              <Select.Option value="interval">间隔执行</Select.Option>
                            </Select>
                          </Form.Item>

                          <Form.Item
                            name="hour"
                            label="小时"
                            rules={[{ required: true }]}
                          >
                            <InputNumber min={0} max={23} placeholder="0-23" style={{ width: 100 }} />
                          </Form.Item>

                          <Form.Item
                            name="minute"
                            label="分钟"
                            rules={[{ required: true }]}
                          >
                            <InputNumber min={0} max={59} placeholder="0-59" style={{ width: 100 }} />
                          </Form.Item>

                          <Form.Item
                            name="keyword_id"
                            label="关键词"
                          >
                            <Select
                              style={{ width: 200 }}
                              placeholder="选择关键词（可选）"
                              allowClear
                            >
                              {keywords.map(kw => (
                                <Select.Option key={kw.id} value={kw.id}>
                                  {kw.keyword} ({kw.group_name})
                                </Select.Option>
                              ))}
                            </Select>
                          </Form.Item>

                          <Form.Item
                            name="max_results"
                            label="每个关键词最大结果数"
                            rules={[{ required: true }]}
                          >
                            <InputNumber min={1} max={50} placeholder="默认15" style={{ width: 120 }} />
                          </Form.Item>

                          <Form.Item>
                            <Button
                              type="primary"
                              htmlType="submit"
                              icon={<PlusOutlined />}
                              loading={setupLoading}
                            >
                              添加任务
                            </Button>
                          </Form.Item>
                        </Form>
                      </Card>
                    </Col>

                    {/* 当前任务列表 */}
                    <Col span={24}>
                      <Card
                        title={
                          <Space>
                            <ClockCircleOutlined />
                            <span>当前定时任务</span>
                          </Space>
                        }
                      >
                        <Table
                          columns={columns}
                          dataSource={schedulerStatus?.jobs || []}
                          rowKey="id"
                          pagination={false}
                          locale={{
                            emptyText: '暂无定时任务'
                          }}
                        />
                      </Card>
                    </Col>
                  </Row>
                </div>
              )
            },
            {
              key: 'login',
              label: 'MediaCrawler 一键启动',
              children: (
                <Card>
                  <Alert
                    title="MediaCrawler 一键启动"
                    description="选择关键词后点击启动，系统将自动配置MediaCrawler并打开浏览器，扫码登录后即可开始爬取数据。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Row gutter={16}>
                    <Col span={12}>
                      <Card title="1. 选择关键词">
                        <p style={{ marginBottom: 16 }}>
                          请选择要爬取的关键词：
                        </p>
                        <Select
                          mode="multiple"
                          style={{ width: '100%', marginBottom: 16 }}
                          placeholder="选择关键词"
                          value={selectedKeywords}
                          onChange={setSelectedKeywords}
                          options={keywords.filter(kw => kw.is_active).map(kw => ({
                            label: kw.keyword,
                            value: kw.keyword
                          }))}
                        />

                        <div style={{ marginTop: 16 }}>
                          <span style={{ marginRight: 8 }}>爬取数量：</span>
                          <InputNumber
                            min={1}
                            max={50}
                            value={crawlCount}
                            onChange={(value) => setCrawlCount(value || 15)}
                            placeholder="每个关键词数量"
                          />
                        </div>
                      </Card>
                    </Col>

                    <Col span={12}>
                      <Card title="2. 一键启动">
                        <p style={{ marginBottom: 16 }}>
                          点击下方按钮启动MediaCrawler：
                        </p>

                        {/* 爬取状态指示器 */}
                        {isCrawling && (
                          <Alert
                            message={
                              <Space>
                                <SyncOutlined spin />
                                <span>正在爬取数据... 已运行 {Math.floor((new Date().getTime() - (crawlStartTime?.getTime() || new Date().getTime())) / 1000)} 秒</span>
                              </Space>
                            }
                            description="系统将自动检测爬取完成状态，请耐心等待..."
                            type="info"
                            showIcon
                            style={{ marginBottom: 16 }}
                          />
                        )}

                        {/* 爬取完成标识 */}
                        {crawlCompleted && (
                          <Alert
                            message="✅ 数据爬取已完成"
                            description={
                              <Space>
                                <span>发现新数据文件</span>
                                <Button size="small" onClick={() => setActiveTab('import')}>
                                  前往导入
                                </Button>
                              </Space>
                            }
                            type="success"
                            showIcon
                            style={{ marginBottom: 16 }}
                          />
                        )}

                        <Space orientation="vertical" style={{ width: '100%' }} size="large">
                          <Button
                            type="primary"
                            size="large"
                            icon={<CloudSyncOutlined />}
                            onClick={handleQuickStart}
                            disabled={isCrawling}
                            block
                          >
                            一键启动（扫码登录 + 爬虫）
                          </Button>

                          <Divider style={{ margin: '12px 0' }} />

                          <Button
                            icon={<SyncOutlined />}
                            onClick={handleLoginOnly}
                            style={{ width: '100%' }}
                          >
                            仅登录（首次使用）
                          </Button>

                          <Button
                            danger
                            icon={<ExclamationCircleOutlined />}
                            onClick={handleLogout}
                            style={{ width: '100%' }}
                          >
                            重置登录状态
                          </Button>
                        </Space>
                      </Card>
                    </Col>
                  </Row>

                  <Divider />

                  <Card title="使用说明">
                    <Row gutter={16}>
                      <Col span={8}>
                        <Card size="small" title="首次使用">
                          <ol>
                            <li>选择关键词</li>
                            <li>点击"仅登录"按钮</li>
                            <li>浏览器打开后扫码登录</li>
                            <li>登录成功后关闭浏览器</li>
                            <li>以后直接一键启动即可</li>
                          </ol>
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small" title="日常使用">
                          <ol>
                            <li>选择要爬取的关键词</li>
                            <li>设置爬取数量</li>
                            <li>点击"一键启动"</li>
                            <li>扫码确认登录</li>
                            <li>自动开始爬取数据</li>
                          </ol>
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small" title="登录状态">
                          <Space orientation="vertical">
                            <div>
                              状态：{loginStatus === 'logged_in' ?
                                <Tag color="success" icon={<CheckCircleOutlined />}>已登录</Tag> :
                                loginStatus === 'logged_out' ?
                                <Tag color="error" icon={<ExclamationCircleOutlined />}>未登录</Tag> :
                                <Tag color="default">检查中...</Tag>
                              }
                            </div>
                            <Button
                              size="small"
                              icon={<SyncOutlined />}
                              onClick={handleCheckLoginStatus}
                            >
                              检查登录状态
                            </Button>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                  </Card>
                </Card>
              )
            },
            {
              key: 'import',
              label: '数据导入',
              children: (
                <Card>
                  <Alert
                    title="数据导入功能"
                    description="将MediaCrawler爬取的数据导入到项目数据库中，支持查看和管理爬取的内容。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Row gutter={16}>
                    <Col span={12}>
                      <Card title="数据概览">
                        {dataSummary ? (
                          <Descriptions bordered column={1}>
                            <Descriptions.Item label="数据文件">
                              {dataSummary.latest_file || '无'}
                            </Descriptions.Item>
                            <Descriptions.Item label="记录数量">
                              {dataSummary.file_count || 0} 条
                            </Descriptions.Item>
                            <Descriptions.Item label="文件大小">
                              {dataSummary.file_size ? `${(dataSummary.file_size / 1024).toFixed(2)} KB` : '0 KB'}
                            </Descriptions.Item>
                            <Descriptions.Item label="更新时间">
                              {dataSummary.modified_time ? new Date(dataSummary.modified_time).toLocaleString('zh-CN') : '-'}
                            </Descriptions.Item>
                          </Descriptions>
                        ) : (
                          <p>正在加载数据概览...</p>
                        )}
                      </Card>
                    </Col>

                    <Col span={12}>
                      <Card title="导入数据">
                        <p style={{ marginBottom: 16 }}>
                          选择关键词将爬取的数据导入到数据库：
                        </p>
                        <Select
                          style={{ width: '100%', marginBottom: 16 }}
                          placeholder="选择关键词"
                          onChange={(value) => {
                            if (value) {
                              handleImportData(value);
                            }
                          }}
                          loading={dataImportLoading}
                        >
                          {keywords.filter(kw => kw.is_active).map(kw => (
                            <Select.Option key={kw.id} value={kw.keyword}>
                              {kw.keyword}
                            </Select.Option>
                          ))}
                        </Select>

                        <Button
                          icon={<SyncOutlined />}
                          onClick={loadDataSummary}
                          style={{ width: '100%' }}
                        >
                          刷新数据概览
                        </Button>
                      </Card>
                    </Col>
                  </Row>

                  <Divider />

                  <Card title="删除数据">
                    <Alert
                      message="清理数据"
                      description="删除指定关键词的数据文件和数据库记录，用于清理测试数据或重新开始爬取。"
                      type="warning"
                      showIcon
                      style={{ marginBottom: 16 }}
                    />

                    <Row gutter={16}>
                      <Col span={12}>
                        <p style={{ marginBottom: 16 }}>
                          选择要删除数据的关键词：
                        </p>
                        <Select
                          style={{ width: '100%', marginBottom: 16 }}
                          placeholder="选择关键词"
                          value={selectedKeywordForDelete}
                          onChange={setSelectedKeywordForDelete}
                        >
                          {keywords.filter(kw => kw.is_active).map(kw => (
                            <Select.Option key={kw.id} value={kw.keyword}>
                              {kw.keyword}
                            </Select.Option>
                          ))}
                        </Select>
                      </Col>

                      <Col span={12}>
                        <p style={{ marginBottom: 16 }}>
                          选择删除类型：
                        </p>
                        <Radio.Group
                          value={deleteType}
                          onChange={(e) => setDeleteType(e.target.value)}
                          style={{ marginBottom: 16 }}
                        >
                          <Space orientation="vertical">
                            <Radio value="all">删除文件和数据库数据</Radio>
                            <Radio value="file">只删除数据文件</Radio>
                            <Radio value="database">只删除数据库数据</Radio>
                          </Space>
                        </Radio.Group>
                      </Col>
                    </Row>

                    <Button
                      type="primary"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={handleDeleteData}
                      loading={deleteLoading}
                      disabled={!selectedKeywordForDelete}
                      block
                      style={{ marginTop: 16 }}
                    >
                      删除数据
                    </Button>
                  </Card>

                  <Divider />

                  <Card title="使用说明">
                    <ol>
                      <li>确保MediaCrawler已经完成爬取任务</li>
                      <li>数据会保存在MediaCrawler的data目录下</li>
                      <li>选择对应的关键词点击导入按钮</li>
                      <li>导入成功后可以在"内容管理"页面查看数据</li>
                      <li>支持重复导入，系统会自动更新已存在的数据</li>
                      <li>删除功能可清理测试数据，确保统计显示真实爬取数据</li>
                    </ol>
                  </Card>
                </Card>
              )
            },
            {
              key: 'statistics',
              label: '爬虫数据统计',
              children: (
                <Card>
                  <Alert
                    title="真实数据统计"
                    description="展示从小红书爬取的真实数据统计信息，按关键词分类显示帖子、点赞、收藏等数据。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  {statisticsLoading ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                      <Spin size="large" />
                      <div style={{ marginTop: '16px' }}>正在加载统计数据...</div>
                    </div>
                  ) : crawlStatistics && crawlStatistics.success ? (
                    <div>
                      {crawlStatistics.statistics && crawlStatistics.statistics.length > 0 ? (
                        <Row gutter={[16, 16]}>
                          {crawlStatistics.statistics.map((stat: any, index: number) => (
                            <Col span={24} key={index}>
                              <Card
                                title={<span style={{ fontWeight: 'bold' }}>{stat.keyword}</span>}
                                extra={
                                  <Tag color="blue">{stat.total_posts} 条帖子</Tag>
                                }
                                style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                              >
                                <Row gutter={16}>
                                  <Col span={6}>
                                    <Statistic
                                      title="总点赞数"
                                      value={stat.total_likes}
                                      prefix={<LikeOutlined />}
                                      styles={{ content: { color: '#3f8600' } }}
                                    />
                                  </Col>
                                  <Col span={6}>
                                    <Statistic
                                      title="总收藏数"
                                      value={stat.total_collects}
                                      prefix={<StarOutlined />}
                                      styles={{ content: { color: '#cf1322' } }}
                                    />
                                  </Col>
                                  <Col span={6}>
                                    <Statistic
                                      title="总评论数"
                                      value={stat.total_comments}
                                      prefix={<MessageOutlined />}
                                      styles={{ content: { color: '#1890ff' } }}
                                    />
                                  </Col>
                                  <Col span={6}>
                                    <Statistic
                                      title="最高点赞"
                                      value={stat.max_likes}
                                      prefix={<FireOutlined />}
                                      styles={{ content: { color: '#fa541c' } }}
                                    />
                                  </Col>
                                </Row>

                                <Divider />

                                <Row gutter={16}>
                                  <Col span={8}>
                                    <Card size="small" title="平均数据">
                                      <p>平均点赞: <strong>{stat.avg_likes}</strong></p>
                                      <p>平均收藏: <strong>{stat.avg_collects}</strong></p>
                                      <p>平均评论: <strong>{stat.avg_comments}</strong></p>
                                    </Card>
                                  </Col>
                                  <Col span={16}>
                                    <Card size="small" title="最新爬取的帖子">
                                      {stat.latest_posts && stat.latest_posts.length > 0 ? (
                                        <List
                                          size="small"
                                          dataSource={stat.latest_posts}
                                          renderItem={(post: any) => (
                                            <List.Item>
                                              <List.Item.Meta
                                                title={<a href={post.url} target="_blank" rel="noopener noreferrer">{post.title}</a>}
                                                description={
                                                  <div>
                                                    <Space size="large">
                                                      <span><LikeOutlined /> {post.likes}</span>
                                                      <span><StarOutlined /> {post.collects}</span>
                                                      <span><MessageOutlined /> {post.comments}</span>
                                                      <span>{post.author}</span>
                                                    </Space>
                                                  </div>
                                                }
                                              />
                                            </List.Item>
                                          )}
                                        />
                                      ) : (
                                        <p>暂无最新数据</p>
                                      )}
                                    </Card>
                                  </Col>
                                </Row>
                              </Card>
                            </Col>
                          ))}
                        </Row>
                      ) : (
                        <Card>
                          <p style={{ textAlign: 'center', padding: '20px' }}>
                            暂无统计数据，请先进行数据爬取和导入
                          </p>
                        </Card>
                      )}
                    </div>
                  ) : (
                    <Card>
                      <p style={{ textAlign: 'center', padding: '20px' }}>
                        加载统计数据失败，请稍后重试
                      </p>
                    </Card>
                  )}

                  <Divider />

                  <Button
                    icon={<SyncOutlined />}
                    onClick={loadCrawlStatistics}
                    loading={statisticsLoading}
                  >
                    刷新统计数据
                  </Button>
                </Card>
              )
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default CrawlerPage;