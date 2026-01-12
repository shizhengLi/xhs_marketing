import request from '../utils/request';

export interface Post {
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
  published_at?: string;
  crawled_at?: string;
  keyword_name?: string;
}

export interface PostsResponse {
  total: number;
  posts: Post[];
}

export interface PostStats {
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

export const postsService = {
  /**
   * 获取帖子列表
   */
  getPosts: (params?: {
    keyword_id?: number;
    keyword_name?: string;
    sort_by?: string;
    order?: string;
    limit?: number;
    offset?: number;
    min_likes?: number;
  }) => {
    return request.get<PostsResponse>('/v1/posts/', { params }) as Promise<PostsResponse>;
  },

  /**
   * 获取帖子统计信息
   */
  getStats: (keyword_id?: number) => {
    return request.get<PostStats>('/v1/posts/stats', {
      params: keyword_id ? { keyword_id } : {}
    }) as Promise<PostStats>;
  },

  /**
   * 获取热门趋势帖子
   */
  getTrending: (params?: {
    keyword_id?: number;
    days?: number;
    limit?: number;
  }) => {
    return request.get('/v1/posts/trending', { params }) as Promise<any>;
  }
};