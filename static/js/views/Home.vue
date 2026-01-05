/**
 * 首页组件
 */
<template>
  <div class="home">
    <div class="article-list" v-if="articles.length > 0">
      <article class="article-card" v-for="article in articles" :key="article.id">
        <h2>
          <a :href="'/article/' + article.slug">{{ article.title }}</a>
        </h2>
        <div class="article-meta">
          <span v-if="article.category_name">{{ article.category_name }}</span>
          <span v-if="article.author_name"> | {{ article.author_name }}</span>
          <span> | {{ formatDate(article.published_at) }}</span>
          <span> | 阅读: {{ article.view_count }}</span>
        </div>
        <p class="article-excerpt">{{ article.excerpt }}</p>
        <div class="article-actions">
          <a :href="'/article/' + article.slug" class="btn btn-primary btn-small">阅读全文</a>
        </div>
      </article>
    </div>

    <div v-else class="no-articles">
      <p>暂无文章</p>
    </div>

    <div class="pagination" v-if="pages > 1">
      <a v-if="page > 1" :href="'/?page=' + (page - 1)">上一页</a>
      <span v-for="p in pages" :key="p" :class="{ active: p === page }">
        <a v-if="p !== page" :href="'/?page=' + p">{{ p }}</a>
        <span v-else>{{ p }}</span>
      </span>
      <a v-if="page < pages" :href="'/?page=' + (page + 1)">下一页</a>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { articlesApi } from '../api/articles';

export default {
  name: 'Home',
  props: {
    initialArticles: {
      type: Array,
      default: () => []
    },
    initialPage: {
      type: Number,
      default: 1
    }
  },
  setup(props) {
    const articles = ref(props.initialArticles);
    const page = ref(props.initialPage);
    const pages = ref(1);

    const fetchArticles = async () => {
      try {
        const response = await articlesApi.getList({ page: page.value });
        articles.value = response.data.articles;
        pages.value = response.data.pages;
      } catch (e) {
        console.error('Failed to fetch articles:', e);
      }
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
      formatDate
    };
  }
};
</script>

<style scoped>
.no-articles {
  text-align: center;
  padding: 50px;
  color: var(--text-light);
  font-size: 1.2em;
}
</style>
