import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Select,
  message,
  Tag,
  Space,
  Row,
  Col,
  Statistic,
  Tabs,
  Typography,
  Divider,
  Alert,
  Modal
} from 'antd';
import {
  LikeOutlined,
  StarOutlined,
  MessageOutlined,
  ShareAltOutlined,
  FireOutlined,
  EyeOutlined,
  FilterOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { postsService } from '../services/posts';
import { keywordService } from '../services/keyword';

// 本地类型定义
interface Post {
  id: number;
  keyword_id: number;
  title: string;
  content?: string;
  author?: string;
  likes: number;
  collects: number;
  comments: number;
  shares: number;
  url?: string;
  video_url?: string;
  video_content?: string;
  published_at?: string;
  crawled_at?: string;
  keyword_name?: string;
}

interface PostStats {
  total_posts: number;
  total_likes: number;
  total_collects: number;
  total_comments: number;
  avg_likes: number;
  avg_collects: number;
  avg_comments: number;
  top_posts: Array<{
    title: string;
    author: string;
    likes: number;
    collects: number;
    comments: number;
    url: string;
  }>;
}

const { Title, Text, Paragraph } = Typography;

const PostsPage: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [keywords, setKeywords] = useState<any[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<number | undefined>();
  const [sortBy, setSortBy] = useState<string>('likes');
  const [order, setOrder] = useState<string>('desc');
  const [stats, setStats] = useState<PostStats | null>(null);
  const [trendingPosts, setTrendingPosts] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('categories');
  const [currentPost, setCurrentPost] = useState<Post | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [groupedPosts, setGroupedPosts] = useState<{ [key: string]: Post[] }>({});

  // 加载关键词列表
  const loadKeywords = async () => {
    try {
      const data = await keywordService.getKeywords();
      setKeywords(data);
    } catch (error) {
      message.error('加载关键词列表失败');
    }
  };

  // 加载帖子数据
  const loadPosts = async () => {
    setLoading(true);
    try {
      const response = await postsService.getPosts({
        sort_by: sortBy,
        order: order,
        limit: 200
      });

      setPosts(response.posts);
      setTotal(response.total);

      // 按关键词分组帖子
      const grouped: { [key: string]: Post[] } = {};
      response.posts.forEach(post => {
        const keyword = post.keyword_name || '未知关键词';
        if (!grouped[keyword]) {
          grouped[keyword] = [];
        }
        grouped[keyword].push(post);
      });
      setGroupedPosts(grouped);
    } catch (error) {
      message.error('加载帖子数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStats = async () => {
    try {
      const data = await postsService.getStats(selectedKeyword);
      setStats(data);
    } catch (error) {
      console.error('加载统计数据失败:', error);
    }
  };

  // 加载热门帖子
  const loadTrendingPosts = async () => {
    try {
      const response = await postsService.getTrending({
        keyword_id: selectedKeyword,
        days: 7,
        limit: 20
      });
      setTrendingPosts(response.posts);
    } catch (error) {
      console.error('加载热门帖子失败:', error);
    }
  };

  useEffect(() => {
    loadKeywords();
  }, []);

  useEffect(() => {
    if (activeTab === 'categories' || activeTab === 'all') {
      loadPosts();
    }
  }, [activeTab, sortBy, order]);

  useEffect(() => {
    loadStats();
    loadTrendingPosts();
  }, [selectedKeyword]);

  // 格式化数字
  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return `${(num / 10000).toFixed(1)}万`;
    }
    return num.toLocaleString();
  };

  // 查看详情
  const viewDetail = (post: Post) => {
    setCurrentPost(post);
    setDetailModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
      render: (text: string, record: Post) => (
        <a onClick={() => viewDetail(record)} style={{ fontWeight: 500 }}>
          {record.video_url && (
            <Tag color="purple" style={{ marginRight: 8 }}>视频</Tag>
          )}
          {text}
        </a>
      )
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: '10%',
      render: (text: string) => <Text>{text || '匿名'}</Text>
    },
    {
      title: '热度',
      key: 'heat',
      width: '40%',
      render: (_: any, record: Post) => (
        <Space size="large">
          <span>
            <LikeOutlined style={{ color: '#ff4d4f' }} /> {formatNumber(record.likes)}
          </span>
          <span>
            <StarOutlined style={{ color: '#faad14' }} /> {formatNumber(record.collects)}
          </span>
          <span>
            <MessageOutlined style={{ color: '#1890ff' }} /> {formatNumber(record.comments)}
          </span>
          <span>
            <ShareAltOutlined style={{ color: '#52c41a' }} /> {formatNumber(record.shares)}
          </span>
        </Space>
      )
    },
    {
      title: '关键词',
      dataIndex: 'keyword_name',
      key: 'keyword_name',
      width: '10%',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '操作',
      key: 'actions',
      width: '10%',
      render: (_: any, record: Post) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => viewDetail(record)}
          >
            详情
          </Button>
          {record.url && (
            <Button
              type="link"
              onClick={() => window.open(record.url, '_blank')}
            >
              原文
            </Button>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <FireOutlined />
            <span>小红书热点内容</span>
          </Space>
        }
        extra={
          <Space>
            <Select
              style={{ width: 150 }}
              placeholder="选择关键词"
              allowClear
              value={selectedKeyword}
              onChange={setSelectedKeyword}
            >
              {keywords.map(kw => (
                <Select.Option key={kw.id} value={kw.id}>
                  {kw.keyword}
                </Select.Option>
              ))}
            </Select>
            <Select
              style={{ width: 120 }}
              value={sortBy}
              onChange={setSortBy}
            >
              <Select.Option value="likes">点赞数</Select.Option>
              <Select.Option value="collects">收藏数</Select.Option>
              <Select.Option value="comments">评论数</Select.Option>
              <Select.Option value="shares">分享数</Select.Option>
              <Select.Option value="published_at">发布时间</Select.Option>
            </Select>
            <Select
              style={{ width: 100 }}
              value={order}
              onChange={setOrder}
            >
              <Select.Option value="desc">降序</Select.Option>
              <Select.Option value="asc">升序</Select.Option>
            </Select>
            <Button
              icon={<FilterOutlined />}
              onClick={loadPosts}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'categories',
              label: `按关键词分类 (${total})`,
              children: (
                <div>
                  <Alert
                    message="热点内容分类展示"
                    description="按照不同关键词类别分别展示新增的热点内容，方便对比分析各领域趋势。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  {loading ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                     加载中...
                    </div>
                  ) : Object.keys(groupedPosts).length > 0 ? (
                    <Row gutter={[16, 16]}>
                      {Object.entries(groupedPosts).map(([keyword, keywordPosts]) => (
                        <Col span={24} key={keyword}>
                          <Card
                            title={
                              <Space>
                                <Tag color="blue" style={{ fontSize: '16px', padding: '4px 12px' }}>
                                  {keyword}
                                </Tag>
                                <span style={{ fontSize: '14px', color: '#666' }}>
                                  {keywordPosts.length} 条内容
                                </span>
                              </Space>
                            }
                            extra={
                              <Button
                                size="small"
                                onClick={() => {
                                  setSelectedKeyword(keywords.find(k => k.keyword === keyword)?.id);
                                  setActiveTab('all');
                                }}
                              >
                                查看全部
                              </Button>
                            }
                            style={{
                              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                              borderRadius: '8px'
                            }}
                          >
                            {/* 显示该关键词的热度统计 */}
                            <Row gutter={16} style={{ marginBottom: 16 }}>
                              <Col span={6}>
                                <Statistic
                                  title="总点赞数"
                                  value={keywordPosts.reduce((sum, p) => sum + p.likes, 0)}
                                  prefix={<LikeOutlined />}
                                  styles={{ content: { color: '#ff4d4f', fontSize: '20px' } }}
                                  valueStyle={{ fontSize: '20px' }}
                                />
                              </Col>
                              <Col span={6}>
                                <Statistic
                                  title="总收藏数"
                                  value={keywordPosts.reduce((sum, p) => sum + p.collects, 0)}
                                  prefix={<StarOutlined />}
                                  styles={{ content: { color: '#faad14', fontSize: '20px' } }}
                                  valueStyle={{ fontSize: '20px' }}
                                />
                              </Col>
                              <Col span={6}>
                                <Statistic
                                  title="总评论数"
                                  value={keywordPosts.reduce((sum, p) => sum + p.comments, 0)}
                                  prefix={<MessageOutlined />}
                                  styles={{ content: { color: '#1890ff', fontSize: '20px' } }}
                                  valueStyle={{ fontSize: '20px' }}
                                />
                              </Col>
                              <Col span={6}>
                                <Statistic
                                  title="最高点赞"
                                  value={Math.max(...keywordPosts.map(p => p.likes), 0)}
                                  prefix={<FireOutlined />}
                                  styles={{ content: { color: '#ff7a45', fontSize: '20px' } }}
                                  valueStyle={{ fontSize: '20px' }}
                                />
                              </Col>
                            </Row>

                            <Divider style={{ margin: '16px 0' }} />

                            {/* 显示该关键词下最热门的帖子 */}
                            <div style={{ marginBottom: 8 }}>
                              <Text strong style={{ fontSize: '14px' }}>热门内容：</Text>
                            </div>

                            {keywordPosts.slice(0, 3).map((post, index) => (
                              <Card
                                key={post.id}
                                size="small"
                                style={{
                                  marginBottom: index < keywordPosts.slice(0, 3).length - 1 ? '12px' : '0',
                                  border: '1px solid #f0f0f0',
                                  borderRadius: '6px',
                                  transition: 'all 0.3s',
                                  cursor: 'pointer'
                                }}
                                hoverable
                                onClick={() => viewDetail(post)}
                              >
                                <Row gutter={16} align="middle">
                                  <Col span={16}>
                                    <div style={{ marginBottom: 4 }}>
                                      <Tag color="red" style={{ marginRight: 8 }}>
                                        TOP {index + 1}
                                      </Tag>
                                      <Text strong ellipsis={{ tooltip: post.title }} style={{ fontSize: '14px' }}>
                                        {post.title}
                                      </Text>
                                    </div>
                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                      作者：{post.author || '匿名'}
                                    </Text>
                                  </Col>
                                  <Col span={8}>
                                    <Row justify="end">
                                      <Col>
                                        <Space size="large">
                                          <span style={{ fontSize: '14px' }}>
                                            <LikeOutlined style={{ color: '#ff4d4f' }} /> {formatNumber(post.likes)}
                                          </span>
                                          <span style={{ fontSize: '14px' }}>
                                            <StarOutlined style={{ color: '#faad14' }} /> {formatNumber(post.collects)}
                                          </span>
                                          <span style={{ fontSize: '14px' }}>
                                            <MessageOutlined style={{ color: '#1890ff' }} /> {formatNumber(post.comments)}
                                          </span>
                                        </Space>
                                      </Col>
                                    </Row>
                                  </Col>
                                </Row>
                              </Card>
                            ))}

                            {keywordPosts.length > 3 && (
                              <div style={{ textAlign: 'center', marginTop: '12px' }}>
                                <Button
                                  type="link"
                                  onClick={() => {
                                    setSelectedKeyword(keywords.find(k => k.keyword === keyword)?.id);
                                    setActiveTab('all');
                                  }}
                                >
                                  查看更多 ({keywordPosts.length - 3} 条)
                                </Button>
                              </div>
                            )}
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  ) : (
                    <Card>
                      <p style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                        暂无数据，请先进行数据爬取
                      </p>
                    </Card>
                  )}
                </div>
              )
            },
            {
              key: 'all',
              label: `全部内容 (${total})`,
              children: (
                <div>
                  {stats && (
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                      <Col span={4}>
                        <Statistic
                          title="总帖子数"
                          value={stats.total_posts}
                          prefix={<FileTextOutlined />}
                          styles={{ content: { fontSize: '20px' } }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="总点赞数"
                          value={stats.total_likes}
                          prefix={<LikeOutlined />}
                          formatter={(value) => formatNumber(Number(value))}
                          styles={{ content: { fontSize: '20px' } }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="总收藏数"
                          value={stats.total_collects}
                          prefix={<StarOutlined />}
                          formatter={(value) => formatNumber(Number(value))}
                          styles={{ content: { fontSize: '20px' } }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="总评论数"
                          value={stats.total_comments}
                          prefix={<MessageOutlined />}
                          formatter={(value) => formatNumber(Number(value))}
                          styles={{ content: { fontSize: '20px' } }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="平均点赞"
                          value={stats.avg_likes}
                          precision={1}
                          formatter={(value) => formatNumber(Number(value))}
                          styles={{ content: { fontSize: '20px' } }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="平均收藏"
                          value={stats.avg_collects}
                          precision={1}
                          formatter={(value) => formatNumber(Number(value))}
                          styles={{ content: { fontSize: '20px' } }}
                        />
                      </Col>
                    </Row>
                  )}

                  <Table
                    columns={columns}
                    dataSource={posts}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                      total: total,
                      pageSize: 20,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total) => `共 ${total} 条`
                    }}
                  />
                </div>
              )
            },
            {
              key: 'trending',
              label: '热门趋势',
              children: (
                <div>
                  <Alert
                    title="热门趋势"
                    description={`基于最近7天的数据，按综合热度排序（点赞 + 收藏×2 + 评论）`}
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />

                  <Row gutter={[16, 16]}>
                    {trendingPosts.map((post, index) => (
                      <Col span={12} key={index}>
                        <Card
                          size="small"
                          title={
                            <Space>
                              <Tag color={index < 3 ? 'red' : 'blue'}>
                                {index + 1}
                              </Tag>
                              <Text ellipsis style={{ maxWidth: 400 }}>
                                {post.title}
                              </Text>
                            </Space>
                          }
                          extra={
                            <Text type="secondary">
                              热度: {formatNumber(post.heat_score)}
                            </Text>
                          }
                        >
                          <Space direction="vertical" style={{ width: '100%' }}>
                            <Text>作者: {post.author}</Text>
                            <Space>
                              <LikeOutlined /> {formatNumber(post.likes)}
                              <StarOutlined /> {formatNumber(post.collects)}
                              <MessageOutlined /> {formatNumber(post.comments)}
                            </Space>
                            <Text type="secondary" ellipsis>
                              {post.content}
                            </Text>
                            <Space>
                              <Tag color="green">{post.keyword_name}</Tag>
                              <Button
                                type="link"
                                size="small"
                                onClick={() => window.open(post.url, '_blank')}
                              >
                                查看原文
                              </Button>
                            </Space>
                          </Space>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </div>
              )
            }
          ]}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="帖子详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {currentPost && (
          <div>
            <Title level={4}>{currentPost.title}</Title>
            <Divider />
            <Row gutter={16}>
              <Col span={12}>
                <Space direction="vertical">
                  <Text><strong>作者:</strong> {currentPost.author}</Text>
                  <Text><strong>关键词:</strong> <Tag>{currentPost.keyword_name}</Tag></Text>
                  <Text><strong>点赞:</strong> {formatNumber(currentPost.likes)}</Text>
                  <Text><strong>收藏:</strong> {formatNumber(currentPost.collects)}</Text>
                </Space>
              </Col>
              <Col span={12}>
                <Space direction="vertical">
                  <Text><strong>评论:</strong> {formatNumber(currentPost.comments)}</Text>
                  <Text><strong>分享:</strong> {formatNumber(currentPost.shares)}</Text>
                  <Text><strong>发布时间:</strong> {currentPost.published_at ? new Date(currentPost.published_at).toLocaleString('zh-CN') : '-'}</Text>
                  <Text><strong>爬取时间:</strong> {currentPost.crawled_at ? new Date(currentPost.crawled_at).toLocaleString('zh-CN') : '-'}</Text>
                </Space>
              </Col>
            </Row>
            <Divider />
            <Title level={5}>内容</Title>
            <Paragraph style={{ maxHeight: 300, overflow: 'auto' }}>
              {currentPost.content || '暂无内容'}
            </Paragraph>

            {/* 视频内容展示 */}
            {currentPost.video_url && (
              <>
                <Divider />
                <Title level={5}>
                  <Space>
                    <FileTextOutlined />
                    视频内容
                  </Space>
                </Title>

                {currentPost.video_content ? (
                  <div style={{
                    padding: '12px',
                    backgroundColor: '#f6f7f9',
                    borderRadius: '6px',
                    border: '1px solid #e8e8e8'
                  }}>
                    <Paragraph
                      style={{
                        maxHeight: 200,
                        overflow: 'auto',
                        margin: 0,
                        fontSize: '14px',
                        lineHeight: '1.6'
                      }}
                    >
                      <Text strong style={{ color: '#1890ff' }}>AI分析内容：</Text>
                      {currentPost.video_content}
                    </Paragraph>
                  </div>
                ) : (
                  <Alert
                    message="视频内容未提取"
                    description="该视频可能超过30秒或内容提取失败，仅显示原始文本内容。"
                    type="info"
                    showIcon
                  />
                )}

                <div style={{ marginTop: '12px' }}>
                  <Button
                    icon={<EyeOutlined />}
                    onClick={() => window.open(currentPost.video_url, '_blank')}
                  >
                    观看原视频
                  </Button>
                </div>
              </>
            )}

            {currentPost.url && !currentPost.video_url && (
              <Button
                type="primary"
                onClick={() => window.open(currentPost.url, '_blank')}
                block
                style={{ marginTop: '16px' }}
              >
                查看原文
              </Button>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PostsPage;