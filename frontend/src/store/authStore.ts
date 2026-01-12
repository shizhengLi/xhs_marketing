import { create } from 'zustand';
import { authService } from '../services/auth';

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: authService.isAuthenticated(),
  isLoading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokenData = await authService.login(username, password);

      // 确保保存token
      if (tokenData && tokenData.access_token) {
        authService.saveToken(tokenData.access_token);

        // 获取用户信息
        const user = await authService.getCurrentUser();
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
      } else {
        throw new Error('登录响应格式错误');
      }
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || '登录失败'
      });
      throw error;
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await authService.register({ username, email, password });
      set({ isLoading: false, error: null });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || '注册失败'
      });
      throw error;
    }
  },

  logout: () => {
    authService.clearToken();
    set({
      user: null,
      isAuthenticated: false,
      error: null
    });
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true, error: null });
    try {
      const user = await authService.getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
    } catch (error: any) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error.message || '获取用户信息失败'
      });
    }
  },

  clearError: () => set({ error: null })
}));