import request from '../utils/request';

export const crawlerService = {
  /**
   * 根据关键词ID抓取内容
   */
  crawlByKeyword: (keywordId: number, count: number = 20) => {
    return request.post(`/v1/crawler/crawl/${keywordId}`, null, {
      params: { count }
    });
  },

  /**
   * 批量抓取
   */
  batchCrawl: (keywordIds: number[], countPerKeyword: number = 20) => {
    return request.post('/v1/crawler/crawl/batch', {
      keyword_ids: keywordIds,
      count_per_keyword: countPerKeyword
    });
  },

  /**
   * 获取关键词的抓取内容
   */
  getPosts: (keywordId: number, params?: {
    limit?: number;
    offset?: number;
    min_likes?: number;
  }) => {
    return request.get(`/v1/crawler/posts/${keywordId}`, { params });
  },

  /**
   * 获取关键词的趋势分析
   */
  getTrends: (keywordId: number) => {
    return request.get(`/v1/crawler/trends/${keywordId}`);
  }
};

export const schedulerService = {
  /**
   * 启动调度器
   */
  start: () => {
    return request.post('/v1/scheduler/start');
  },

  /**
   * 停止调度器
   */
  stop: () => {
    return request.post('/v1/scheduler/stop');
  },

  /**
   * 获取调度器状态
   */
  getStatus: () => {
    return request.get('/v1/scheduler/status');
  },

  /**
   * 设置定时任务
   */
  setupSchedule: (data: {
    hour: number;
    minute: number;
    keyword_id?: number | null;
    schedule_type: 'daily' | 'interval';
    max_results?: number;
  }) => {
    return request.post('/v1/scheduler/setup', data);
  },

  /**
   * 删除定时任务
   */
  deleteJob: (jobId: string) => {
    return request.delete(`/v1/scheduler/jobs/${jobId}`);
  },

  /**
   * 测试爬取关键词
   */
  testCrawl: (keywordId: number) => {
    return request.post(`/v1/scheduler/test-crawl/${keywordId}`);
  }
};

export const mediacrawlerService = {
  /**
   * 一键启动爬虫
   */
  startCrawler: (keywords: string[], count: number = 15) => {
    return request.post('/v1/mediacrawler/start-crawler', { keywords, count });
  },

  /**
   * 快速启动（扫码登录 + 爬虫）
   */
  quickStart: (keywords: string[], count: number = 15) => {
    return request.post('/v1/mediacrawler/quick-start', {
      keywords,
      count
    });
  },

  /**
   * 仅登录（不爬虫）
   */
  loginOnly: () => {
    return request.post('/v1/mediacrawler/login-only');
  },

  /**
   * 获取配置信息
   */
  getConfigInfo: () => {
    return request.get('/v1/mediacrawler/config-info');
  },

  /**
   * 获取登录状态（保留兼容性）
   */
  getLoginStatus: () => {
    return request.get('/v1/mediacrawler/login-status');
  },

  /**
   * 确认手动登录（保留兼容性）
   */
  confirmLogin: (loginMethod: string, success: boolean) => {
    return request.post('/v1/mediacrawler/confirm-login', { login_method: loginMethod, success });
  },

  /**
   * 重置登录状态（保留兼容性）
   */
  resetLogin: () => {
    return request.post('/v1/mediacrawler/reset-login');
  },

  /**
   * 导入MediaCrawler数据到数据库
   */
  importData: (keyword: string) => {
    return request.post('/v1/mediacrawler/import-data', null, {
      params: { keyword }
    });
  },

  /**
   * 获取数据摘要
   */
  getDataSummary: () => {
    return request.get('/v1/mediacrawler/data-summary');
  },

  /**
   * 获取可导入的关键词
   */
  getAvailableKeywords: () => {
    return request.get('/v1/mediacrawler/available-keywords');
  },

  /**
   * 获取爬虫数据统计
   */
  getCrawlStatistics: (keywordId?: number) => {
    return request.get('/v1/mediacrawler/crawl-statistics', {
      params: keywordId ? { keyword_id: keywordId } : {}
    });
  },

  /**
   * 删除指定关键词的数据
   */
  deleteKeywordData: (keyword: string, deleteType: string = 'all') => {
    return request.delete(`/v1/mediacrawler/delete-data/${keyword}`, {
      params: { delete_type: deleteType }
    });
  }
};