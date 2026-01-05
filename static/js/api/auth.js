/**
 * 认证 API
 */
import api from './index';

export const authApi = {
  // 注册
  register(data) {
    return api.post('/auth/register', data);
  },

  // 登录
  login(data) {
    return api.post('/auth/login', data);
  },

  // 登出
  logout() {
    return api.post('/auth/logout');
  },

  // 获取当前用户
  getMe() {
    return api.get('/auth/me');
  },

  // 修改密码
  changePassword(data) {
    return api.put('/auth/password', data);
  }
};
