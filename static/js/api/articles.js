/**
 * 文章 API
 */
import api from './index';

export const articlesApi = {
  // 获取文章列表
  getList(params = {}) {
    return api.get('/articles', { params });
  },

  // 获取文章详情
  getDetail(slug) {
    return api.get(`/articles/${slug}`);
  },

  // 创建文章
  create(data) {
    return api.post('/articles', data);
  },

  // 更新文章
  update(slug, data) {
    return api.put(`/articles/${slug}`, data);
  },

  // 删除文章
  delete(slug) {
    return api.delete(`/articles/${slug}`);
  },

  // 发布文章
  publish(slug) {
    return api.post(`/articles/${slug}/publish`);
  },

  // 下架文章
  unpublish(slug) {
    return api.post(`/articles/${slug}/unpublish`);
  }
};
