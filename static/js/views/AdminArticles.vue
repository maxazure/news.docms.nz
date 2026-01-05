/**
 * 后台文章管理组件
 */
<template>
  <div class="admin-articles">
    <div class="admin-header">
      <h1>文章管理</h1>
      <router-link to="/admin/articles/new" class="btn btn-primary">新建文章</router-link>
    </div>

    <div class="filter-form">
      <select v-model="status" @change="fetchArticles">
        <option value="">全部状态</option>
        <option value="published">已发布</option>
        <option value="draft">草稿</option>
        <option value="archived">已归档</option>
      </select>
      <input type="text" v-model="search" placeholder="搜索标题..." @input="fetchArticles" />
    </div>

    <div class="data-table">
      <table v-if="articles.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>作者</th>
            <th>分类</th>
            <th>状态</th>
            <th>阅读量</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="article in articles" :key="article.id">
            <td>{{ article.id }}</td>
            <td>{{ article.title }}</td>
            <td>{{ article.author_name }}</td>
            <td>{{ article.category_name || '-' }}</td>
            <td>
              <span class="status-badge" :class="'status-' + article.status">
                {{ getStatusText(article.status) }}
              </span>
            </td>
            <td>{{ article.view_count }}</td>
            <td>{{ formatDate(article.created_at) }}</td>
            <td class="table-actions">
              <a :href="'/article/' + article.slug" target="_blank" class="btn btn-secondary btn-small">查看</a>
              <router-link :to="'/admin/articles/' + article.id + '/edit'" class="btn btn-primary btn-small">编辑</router-link>
              <button @click="deleteArticle(article)" class="btn btn-danger btn-small">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">暂无文章</p>
    </div>

    <div class="pagination" v-if="pages > 1">
      <a v-if="page > 1" @click="page--; fetchArticles()">上一页</a>
      <span>第 {{ page }} / {{ pages }} 页</span>
      <a v-if="page < pages" @click="page++; fetchArticles()">下一页</a>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { articlesApi } from '../api/articles';

export default {
  name: 'AdminArticles',
  setup() {
    const articles = ref([]);
    const page = ref(1);
    const pages = ref(1);
    const status = ref('');
    const search = ref('');

    const fetchArticles = async () => {
      try {
        const params = { page: page.value, status: status.value || undefined, search: search.value || undefined };
        const response = await articlesApi.getList(params);
        articles.value = response.data.articles;
        pages.value = response.data.pages;
      } catch (e) {
        console.error('Failed to fetch articles:', e);
      }
    };

    const deleteArticle = async (article) => {
      if (!confirm(`确定要删除文章 "${article.title}" 吗？`)) return;

      try {
        await articlesApi.delete(article.slug);
        fetchArticles();
      } catch (e) {
        alert(e.response?.data?.error || '删除失败');
      }
    };

    const getStatusText = (status) => {
      const map = { published: '已发布', draft: '草稿', archived: '已归档' };
      return map[status] || status;
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('zh-CN');
    };

    onMounted(() => {
      fetchArticles();
    });

    return {
      articles,
      page,
      pages,
      status,
      search,
      fetchArticles,
      deleteArticle,
      getStatusText,
      formatDate
    };
  }
};
</script>

<style scoped>
.filter-form {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-form select,
.filter-form input {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
}

.no-data {
  text-align: center;
  padding: 30px;
  color: var(--text-light);
}
</style>
