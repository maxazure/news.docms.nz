/**
 * Vue 3 应用入口
 */
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';

// 导入样式
import '../css/main.css';
import '../css/admin.css';

// 导入视图组件
import Home from './views/Home.vue';
import Article from './views/Article.vue';
import Login from './views/Login.vue';
import Register from './views/Register.vue';
import Profile from './views/Profile.vue';
import Admin from './views/Admin.vue';
import AdminDashboard from './views/AdminDashboard.vue';
import AdminArticles from './views/AdminArticles.vue';
import AdminArticleEdit from './views/AdminArticleEdit.vue';
import AdminUsers from './views/AdminUsers.vue';
import AdminCategories from './views/AdminCategories.vue';

// 导入状态管理
import { useAuthStore } from './stores/auth';

// 创建 Pinia
const pinia = createPinia();

// 创建路由
const routes = [
  { path: '/', component: Home, name: 'home' },
  { path: '/article/:slug', component: Article, name: 'article' },
  { path: '/login', component: Login, name: 'login' },
  { path: '/register', component: Register, name: 'register' },
  { path: '/profile', component: Profile, name: 'profile' },
  {
    path: '/admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', component: AdminDashboard, name: 'admin-dashboard' },
      { path: 'articles', component: AdminArticles, name: 'admin-articles' },
      { path: 'articles/new', component: AdminArticleEdit, name: 'admin-article-new' },
      { path: 'articles/:id/edit', component: AdminArticleEdit, name: 'admin-article-edit' },
      { path: 'users', component: AdminUsers, name: 'admin-users' },
      { path: 'categories', component: AdminCategories, name: 'admin-categories' }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 检查是否已登录
  if (!authStore.token) {
    const token = localStorage.getItem('access_token');
    if (token) {
      authStore.token = token;
      await authStore.checkAuth();
    }
  }

  // 需要认证的页面
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  // 需要管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' });
    return;
  }

  next();
});

// 创建并挂载应用
const app = createApp({
  setup() {
    return {};
  },
  template: '<router-view />'
});

app.use(pinia);
app.use(router);
app.mount('#app');

// ==================== 增强交互功能 ====================

// 添加平滑滚动
document.addEventListener('DOMContentLoaded', () => {
  // 为所有内部链接添加平滑滚动
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // 添加滚动指示器
  const createScrollIndicator = () => {
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    document.body.appendChild(indicator);

    window.addEventListener('scroll', () => {
      const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      indicator.style.width = scrollPercent + '%';
    });
  };

  createScrollIndicator();

  // 添加视差滚动效果
  const addParallaxEffect = () => {
    const parallaxElements = document.querySelectorAll('.parallax');

    window.addEventListener('scroll', () => {
      parallaxElements.forEach(element => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        element.style.transform = `translate3d(0, ${rate}px, 0)`;
      });
    });
  };

  addParallaxEffect();

  // 添加滚动触发动画
  const addScrollAnimations = () => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.fade-in-section').forEach(el => {
      observer.observe(el);
    });
  };

  addScrollAnimations();

  // 添加鼠标跟踪效果
  const addMouseFollower = () => {
    const follower = document.createElement('div');
    follower.className = 'mouse-follower';
    document.body.appendChild(follower);

    document.addEventListener('mousemove', (e) => {
      follower.style.left = e.clientX + 'px';
      follower.style.top = e.clientY + 'px';
    });

    document.querySelectorAll('a, button, .article-card').forEach(el => {
      el.addEventListener('mouseenter', () => {
        follower.classList.add('active');
      });
      el.addEventListener('mouseleave', () => {
        follower.classList.remove('active');
      });
    });
  };

  // 添加打字机效果到标题
  const addTypewriterEffect = () => {
    const typewriterElements = document.querySelectorAll('.typewriter');
    typewriterElements.forEach(el => {
      const text = el.textContent;
      el.textContent = '';
      let i = 0;
      const typeInterval = setInterval(() => {
        el.textContent += text.charAt(i);
        i++;
        if (i > text.length) {
          clearInterval(typeInterval);
        }
      }, 50);
    });
  };

  addTypewriterEffect();

  // 添加键盘快捷键增强
  const addKeyboardEnhancements = () => {
    document.addEventListener('keydown', (e) => {
      // Alt + 数字键快速导航
      if (e.altKey) {
        const num = parseInt(e.key);
        if (num >= 1 && num <= 9) {
          const elements = document.querySelectorAll('.article-card');
          if (elements[num - 1]) {
            elements[num - 1].scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      }

      // Ctrl/Cmd + K 聚焦搜索
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('#search-input');
        if (searchInput) {
          searchInput.focus();
        }
      }
    });
  };

  addKeyboardEnhancements();

  // 添加触摸手势支持
  const addTouchGestures = () => {
    let touchStartX = 0;
    let touchStartY = 0;

    document.addEventListener('touchstart', (e) => {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    });

    document.addEventListener('touchend', (e) => {
      const touchEndX = e.changedTouches[0].clientX;
      const touchEndY = e.changedTouches[0].clientY;
      const diffX = touchStartX - touchEndX;
      const diffY = touchStartY - touchEndY;

      // 水平滑动切换页面
      if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
        if (diffX > 0) {
          // 向左滑动 - 下一页
          console.log('Swipe left - next page');
        } else {
          // 向右滑动 - 上一页
          console.log('Swipe right - previous page');
        }
      }
    });
  };

  addTouchGestures();

  // 添加自动保存阅读进度
  const addReadingProgress = () => {
    const articleElements = document.querySelectorAll('.article-detail');
    articleElements.forEach(article => {
      const slug = article.dataset.slug;
      if (!slug) return;

      // 恢复阅读进度
      const savedProgress = localStorage.getItem(`reading_progress_${slug}`);
      if (savedProgress) {
        const scrollPercent = parseInt(savedProgress);
        const scrollHeight = article.scrollHeight;
        window.scrollTo(0, (scrollHeight * scrollPercent) / 100);
      }

      // 保存阅读进度
      const saveProgress = () => {
        const scrollPercent = Math.round((window.scrollY / (article.scrollHeight - window.innerHeight)) * 100);
        localStorage.setItem(`reading_progress_${slug}`, scrollPercent);
      };

      window.addEventListener('scroll', debounce(saveProgress, 1000));
    });
  };

  addReadingProgress();

  // 添加懒加载增强
  const enhanceLazyLoading = () => {
    const images = document.querySelectorAll('img[loading="lazy"]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    });

    images.forEach(img => {
      img.addEventListener('load', () => {
        img.classList.add('loaded');
      });
      imageObserver.observe(img);
    });
  };

  enhanceLazyLoading();

  // 添加磁性吸附效果
  const addMagneticEffect = () => {
    const magneticElements = document.querySelectorAll('.magnetic');

    magneticElements.forEach(element => {
      element.addEventListener('mousemove', (e) => {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        element.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
      });

      element.addEventListener('mouseleave', () => {
        element.style.transform = 'translate(0, 0)';
      });
    });
  };

  addMagneticEffect();

  // 添加波纹效果
  const addRippleEffect = () => {
    const rippleElements = document.querySelectorAll('.ripple');

    rippleElements.forEach(element => {
      element.addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const ripple = document.createElement('span');
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple-effect');

        this.appendChild(ripple);

        setTimeout(() => {
          ripple.remove();
        }, 600);
      });
    });
  };

  addRippleEffect();
});

// 工具函数：防抖
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 工具函数：节流
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
