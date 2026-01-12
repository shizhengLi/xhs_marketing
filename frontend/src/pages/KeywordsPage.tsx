import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Tag,
  message,
  Popconfirm,
  Card,
  Typography,
  Tooltip
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  BulbOutlined,
  CloudDownloadOutlined
} from '@ant-design/icons';
import { keywordService } from '../services/keyword';
import { crawlerService } from '../services/crawler';

// 本地类型定义
interface Keyword {
  id: number;
  user_id: number;
  keyword: string;
  group_name: string;
  is_active: boolean;
  is_ai_expanded: boolean;
  created_at: string;
}

const { Title } = Typography;
const { Option } = Select;

const KeywordsPage: React.FC = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingKeyword, setEditingKeyword] = useState<Keyword | null>(null);
  const [aiExpandVisible, setAiExpandVisible] = useState(false);
  const [aiExpandKeyword, setAiExpandKeyword] = useState<string>('');
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [form] = Form.useForm();

  // 获取关键词列表
  const fetchKeywords = async () => {
    setLoading(true);
    try {
      const data = await keywordService.getKeywords();
      setKeywords(data);
    } catch (error) {
      message.error('获取关键词列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeywords();
  }, []);

  // 打开新建模态框
  const handleAdd = () => {
    setEditingKeyword(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 打开编辑模态框
  const handleEdit = (record: Keyword) => {
    setEditingKeyword(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  // 删除关键词
  const handleDelete = async (id: number) => {
    try {
      await keywordService.deleteKeyword(id);
      message.success('删除成功');
      fetchKeywords();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (editingKeyword) {
        // 更新
        await keywordService.updateKeyword(editingKeyword.id, values);
        message.success('更新成功');
      } else {
        // 新建
        await keywordService.createKeyword(values);
        message.success(`关键词 "${values.keyword}" 创建成功`);
      }

      setModalVisible(false);
      fetchKeywords();
    } catch (error: any) {
      // 显示详细的错误信息
      const errorMsg = error.response?.data?.detail || error.message || (editingKeyword ? '更新失败' : '创建失败');
      message.error(errorMsg);
    }
  };

  // AI扩展关键词
  const handleAiExpand = async (keyword: string) => {
    setAiExpandKeyword(keyword);
    setAiExpandVisible(true);
    setAiSuggestions([]);

    try {
      const response = await keywordService.aiExpandKeywords(keyword, 5);
      setAiSuggestions(response.suggested_keywords);
    } catch (error) {
      message.error('AI扩展失败');
    }
  };

  // 使用AI建议的关键词
  const useSuggestion = async (suggestion: string) => {
    try {
      await keywordService.createKeyword({
        keyword: suggestion,
        group_name: 'AI推荐',
        is_active: true
      });
      message.success(`关键词 "${suggestion}" 添加成功`);
      fetchKeywords();
    } catch (error: any) {
      // 显示详细的错误信息
      const errorMsg = error.response?.data?.detail || error.message || '添加失败';
      message.error(errorMsg);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '关键词',
      dataIndex: 'keyword',
      key: 'keyword',
      render: (text: string) => <span style={{ fontWeight: 'bold' }}>{text}</span>
    },
    {
      title: '分组',
      dataIndex: 'group_name',
      key: 'group_name',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: 'AI扩展',
      dataIndex: 'is_ai_expanded',
      key: 'is_ai_expanded',
      render: (isAiExpanded: boolean) => (
        <Tag color={isAiExpanded ? 'purple' : 'default'}>
          {isAiExpanded ? '是' : '否'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: Keyword) => (
        <Space size="small">
          <Tooltip title="AI扩展">
            <Button
              type="primary"
              size="small"
              icon={<BulbOutlined />}
              onClick={() => handleAiExpand(record.keyword)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="default"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个关键词吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="default"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16
        }}>
          <Title level={2} style={{ margin: 0 }}>关键词管理</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            添加关键词
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={keywords}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个关键词`
          }}
        />
      </Card>

      {/* 新建/编辑模态框 */}
      <Modal
        title={editingKeyword ? '编辑关键词' : '添加关键词'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          autoComplete="off"
        >
          <Form.Item
            label="关键词"
            name="keyword"
            rules={[{ required: true, message: '请输入关键词' }]}
          >
            <Input placeholder="请输入关键词" />
          </Form.Item>

          <Form.Item
            label="分组名称"
            name="group_name"
            initialValue="default"
          >
            <Select placeholder="选择分组">
              <Option value="default">默认</Option>
              <Option value="美妆">美妆</Option>
              <Option value="时尚">时尚</Option>
              <Option value="美食">美食</Option>
              <Option value="旅游">旅游</Option>
              <Option value="科技">科技</Option>
              <Option value="生活">生活</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="状态"
            name="is_active"
            valuePropName="checked"
            initialValue={true}
          >
            <Select>
              <Option value={true}>启用</Option>
              <Option value={false}>禁用</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* AI扩展结果模态框 */}
      <Modal
        title={`AI扩展关键词：${aiExpandKeyword}`}
        open={aiExpandVisible}
        onCancel={() => setAiExpandVisible(false)}
        footer={null}
        width={600}
      >
        <div>
          <p>AI为您推荐以下相关关键词：</p>
          <div style={{ marginTop: 16 }}>
            {aiSuggestions.length > 0 ? (
              aiSuggestions.map((suggestion, index) => (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 8,
                    padding: '8px 12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '4px'
                  }}
                >
                  <Tag color="purple" style={{ margin: 0, fontSize: '14px' }}>
                    {suggestion}
                  </Tag>
                  <Button
                    type="primary"
                    size="small"
                    onClick={() => useSuggestion(suggestion)}
                  >
                    添加到监控
                  </Button>
                </div>
              ))
            ) : (
              <p style={{ textAlign: 'center', color: '#999' }}>
                正在生成AI建议...
              </p>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default KeywordsPage;