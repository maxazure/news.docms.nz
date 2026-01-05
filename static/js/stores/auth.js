/**
 * 认证状态管理
 */
import { defineStore } from 'pinia';
import { authApi } from '../api/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },

  actions: {
    async login(username, password) {
      const response = await authApi.login({ username, password });
      const { user, access_token, refresh_token } = response.data;

      this.user = user;
      this.token = access_token;
      this.refreshToken = refresh_token;

      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      return user;
    },

    async register(data) {
      const response = await authApi.register(data);
      const { user, access_token, refresh_token } = response.data;

      this.user = user;
      this.token = access_token;
      this.refreshToken = refresh_token;

      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      return user;
    },

    async logout() {
      try {
        await authApi.logout();
      } catch (e) {
        console.error('Logout error:', e);
      }

      this.user = null;
      this.token = null;
      this.refreshToken = null;

      localStorage.removeItem('user');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },

    async checkAuth() {
      if (!this.token) return false;

      try {
        const response = await authApi.getMe();
        this.user = response.data.user;
        localStorage.setItem('user', JSON.stringify(this.user));
        return true;
      } catch (e) {
        this.logout();
        return false;
      }
    },

    async changePassword(oldPassword, newPassword) {
      await authApi.changePassword({ old_password: oldPassword, new_password: newPassword });
    }
  }
});
