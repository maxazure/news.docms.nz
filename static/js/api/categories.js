/**
 * 分类 API
 */
import api from './index';

export const categoriesApi = {
  // 获取分类列表
  getList() {
    return api.get('/categories');
  },

  // 创建分类
  create(data) {
    return api.post('/categories', data);
  },

  // 更新分类
  update(id, data) {
    return api.put(`/categories/${id}`, data);
  },

  // 删除分类
  delete(id) {
    return api.delete(`/categories/${id}`);
  }
};
