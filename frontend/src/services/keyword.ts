import request from '../utils/request';

export const keywordService = {
  /**
   * 获取关键词列表
   */
  getKeywords: (params?: { group_name?: string; is_active?: boolean }) => {
    return request.get('/v1/keywords/', { params });
  },

  /**
   * 获取单个关键词详情
   */
  getKeyword: (id: number) => {
    return request.get(`/v1/keywords/${id}`);
  },

  /**
   * 创建关键词
   */
  createKeyword: (data: { keyword: string; group_name?: string; is_active?: boolean }) => {
    return request.post('/v1/keywords/', data);
  },

  /**
   * 更新关键词
   */
  updateKeyword: (id: number, data: { keyword?: string; group_name?: string; is_active?: boolean }) => {
    return request.put(`/v1/keywords/${id}`, data);
  },

  /**
   * 删除关键词
   */
  deleteKeyword: (id: number) => {
    return request.delete(`/v1/keywords/${id}`);
  },

  /**
   * AI扩展关键词
   */
  aiExpandKeywords: (baseKeyword: string, count: number = 5) => {
    return request.post('/v1/keywords/ai-expand', {
      base_keyword: baseKeyword,
      count
    });
  }
};