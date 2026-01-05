/**
 * 用户管理 API
 */
import api from './index';

export const usersApi = {
  // 获取用户列表
  getList() {
    return api.get('/admin/users');
  },

  // 获取用户详情
  getDetail(id) {
    return api.get(`/admin/users/${id}`);
  },

  // 更新用户
  update(id, data) {
    return api.put(`/admin/users/${id}`, data);
  },

  // 删除用户
  delete(id) {
    return api.delete(`/admin/users/${id}`);
  },

  // 切换用户激活状态
  toggleActive(id) {
    return api.post(`/admin/users/${id}/toggle-active`);
  },

  // 获取仪表盘统计
  getDashboard() {
    return api.get('/admin/dashboard');
  }
};
