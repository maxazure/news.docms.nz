/**
 * 文章状态管理
 */
import { defineStore } from 'pinia';
import { articlesApi } from '../api/articles';

export const useArticlesStore = defineStore('articles', {
  state: () => ({
    articles: [],
    currentArticle: null,
    total: 0,
    page: 1,
    perPage: 10,
    pages: 0,
    loading: false
  }),

  actions: {
    async fetchArticles(params = {}) {
      this.loading = true;
      try {
        const response = await articlesApi.getList(params);
        const { articles, total, page, per_page, pages } = response.data;

        this.articles = articles;
        this.total = total;
        this.page = page;
        this.perPage = per_page;
        this.pages = pages;
      } catch (e) {
        console.error('Fetch articles error:', e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchArticle(slug) {
      this.loading = true;
      try {
        const response = await articlesApi.getDetail(slug);
        this.currentArticle = response.data.article;
        return this.currentArticle;
      } catch (e) {
        console.error('Fetch article error:', e);
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async createArticle(data) {
      const response = await articlesApi.create(data);
      return response.data.article;
    },

    async updateArticle(slug, data) {
      const response = await articlesApi.update(slug, data);
      return response.data.article;
    },

    async deleteArticle(slug) {
      await articlesApi.delete(slug);
    },

    async publishArticle(slug) {
      const response = await articlesApi.publish(slug);
      return response.data.article;
    },

    async unpublishArticle(slug) {
      const response = await articlesApi.unpublish(slug);
      return response.data.article;
    }
  }
});
