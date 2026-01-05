/**
 * 后台仪表盘组件
 */
<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>仪表盘</h1>
    </div>

    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <h3>{{ stats.total_users }}</h3>
        <p>用户总数</p>
      </div>
      <div class="stat-card">
        <h3>{{ stats.total_articles }}</h3>
        <p>文章总数</p>
      </div>
      <div class="stat-card">
        <h3>{{ stats.published_articles }}</h3>
        <p>已发布</p>
      </div>
      <div class="stat-card">
        <h3>{{ stats.draft_articles }}</h3>
        <p>草稿</p>
      </div>
    </div>

    <div class="recent-section">
      <h2>最近文章</h2>
      <div class="data-table">
        <table v-if="recentArticles.length > 0">
          <thead>
            <tr>
              <th>标题</th>
              <th>作者</th>
              <th>状态</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="article in recentArticles" :key="article.id">
              <td>{{ article.title }}</td>
              <td>{{ article.author_name }}</td>
              <td>
                <span class="status-badge" :class="'status-' + article.status">
                  {{ article.status === 'published' ? '已发布' : '草稿' }}
                </span>
              </td>
              <td>{{ formatDate(article.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">暂无文章</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { usersApi } from '../api/users';

export default {
  name: 'AdminDashboard',
  setup() {
    const stats = ref(null);
    const recentArticles = ref([]);

    const fetchData = async () => {
      try {
        const response = await usersApi.getDashboard();
        stats.value = response.data.stats;
        recentArticles.value = response.data.recent_articles;
      } catch (e) {
        console.error('Failed to fetch dashboard data:', e);
      }
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('zh-CN');
    };

    onMounted(() => {
      fetchData();
    });

    return {
      stats,
      recentArticles,
      formatDate
    };
  }
};
</script>

<style scoped>
.recent-section {
  background: var(--white);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.recent-section h2 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--primary-color);
}

.no-data {
  text-align: center;
  padding: 30px;
  color: var(--text-light);
}
</style>
