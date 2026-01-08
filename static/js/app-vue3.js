/**
 * Vue 3 应用入口 - 浏览器兼容版本
 */

// 全局Vue应用（避免模块系统）
(function() {
  'use strict';

  // 创建简单的Vue 3应用
  const { createApp, ref, reactive, computed, onMounted, watch } = Vue;
  const { createPinia, defineStore } = Pinia;
  const { createRouter, createWebHistory } = VueRouter;

  // 简单的状态管理
  const state = reactive({
    articles: [],
    categories: [],
    loading: false,
    error: null,
    searchQuery: '',
    selectedCategory: null,
    currentPage: 'home'
  });

  // 计算属性
  const isLoggedIn = computed(() => {
    return localStorage.getItem('access_token') !== null;
  });

  const isAdmin = computed(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.role === 'admin';
  });

  // 方法
  function handleSearch() {
    console.log('Search:', state.searchQuery);
    // 实现搜索逻辑
  }

  function filterByCategory(categoryId) {
    state.selectedCategory = categoryId;
    console.log('Filter by category:', categoryId);
  }

  function goToPage(page) {
    console.log('Go to page:', page);
  }

  // 创建Vue应用
  const App = {
    setup() {
      onMounted(() => {
        console.log('Vue 3 App mounted');
        // 添加平滑滚动
        addSmoothScroll();
        // 添加滚动指示器
        createScrollIndicator();
        // 添加交互动画
        addAnimations();
      });

      return {
        state,
        isLoggedIn,
        isAdmin,
        handleSearch,
        filterByCategory,
        goToPage
      };
    },
    template: `
      <div id="app-content">
        <header class="header">
          <div class="container">
            <a href="/" class="logo">
              <span class="logo-icon"></span>
              科技新闻
            </a>
            <nav class="nav">
              <a href="/">首页</a>
              <a v-if="isLoggedIn" href="/admin">管理后台</a>
              <a v-if="!isLoggedIn" href="/login">登录</a>
            </nav>
          </div>
        </header>

        <main class="main">
          <div class="container">
            <div class="search-box">
              <input
                type="search"
                v-model="state.searchQuery"
                @keyup.enter="handleSearch"
                placeholder="搜索文章..."
                class="search-input"
              />
              <button @click="handleSearch" class="search-btn">
                搜索
              </button>
            </div>

            <div v-if="state.loading" class="loading">
              加载中...
            </div>

            <div v-else class="article-list">
              <div v-if="state.articles.length === 0" class="no-articles">
                <p>暂无文章</p>
              </div>
              <article v-for="article in state.articles" :key="article.id" class="article-card">
                <h2>{{ article.title }}</h2>
                <p>{{ article.excerpt || '暂无摘要' }}</p>
              </article>
            </div>
          </div>
        </main>

        <footer class="footer">
          <div class="container">
            <p>&copy; 2026 news.docms.nz - 科技新闻平台</p>
          </div>
        </footer>
      </div>
    `
  };

  // 创建Pinia
  const pinia = createPinia();

  // 创建并挂载应用
  const app = createApp(App);
  app.use(pinia);
  app.mount('#app');

  // 添加增强功能
  function addSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }

  function createScrollIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    document.body.appendChild(indicator);

    window.addEventListener('scroll', () => {
      const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      indicator.style.width = scrollPercent + '%';
    });
  }

  function addAnimations() {
    // 添加滚动动画
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.article-card').forEach(el => {
      observer.observe(el);
    });
  }

  // 全局访问
  window.VueApp = {
    state,
    handleSearch,
    filterByCategory,
    goToPage
  };

  console.log('Vue 3 App initialized');
})();
