// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 关键词类型
export interface Keyword {
  id: number;
  user_id: number;
  keyword: string;
  group_name: string;
  is_active: boolean;
  is_ai_expanded: boolean;
  created_at: string;
}

export interface KeywordCreate {
  keyword: string;
  group_name?: string;
  is_active?: boolean;
}

export interface KeywordUpdate {
  keyword?: string;
  group_name?: string;
  is_active?: boolean;
}

export interface KeywordAIResponse {
  original: string;
  suggested_keywords: string[];
}

// 小红书内容类型
export interface Post {
  id: number;
  keyword_id: number;
  title: string;
  content: string;
  author: string;
  likes: number;
  collects: number;
  comments: number;
  shares: number;
  url: string;
  published_at: string;
  crawled_at: string;
}

// 报告类型
export interface Report {
  id: number;
  user_id: number;
  keyword_id: number;
  title: string;
  content: string;
  summary: string;
  report_date: string;
  created_at: string;
}