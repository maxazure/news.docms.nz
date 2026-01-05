/**
 * 文章详情组件
 */
<template>
  <div class="article-detail" v-if="article">
    <h1>{{ article.title }}</h1>
    <div class="article-meta">
      <span v-if="article.category_name">分类: {{ article.category_name }}</span>
      <span v-if="article.author_name"> | 作者: {{ article.author_name }}</span>
      <span> | 发布于: {{ formatDate(article.published_at) }}</span>
      <span> | 阅读: {{ article.view_count }}</span>
    </div>
    <div class="article-content" v-html="article.html_content"></div>
  </div>
  <div v-else class="loading">
    <p>加载中...</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { articlesApi } from '../api/articles';

export default {
  name: 'Article',
  setup() {
    const article = ref(null);
    const route = useRoute();

    const fetchArticle = async () => {
      try {
        const response = await articlesApi.getDetail(route.params.slug);
        article.value = response.data.article;
      } catch (e) {
        console.error('Failed to fetch article:', e);
      }
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('zh-CN');
    };

    onMounted(() => {
      fetchArticle();
    });

    return {
      article,
      formatDate
    };
  }
};
</script>

<style scoped>
.loading {
  text-align: center;
  padding: 50px;
  color: var(--text-light);
}
</style>
