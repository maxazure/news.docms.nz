/**
 * 后台文章编辑组件
 */
<template>
  <div class="admin-article-edit">
    <div class="admin-header">
      <h1>{{ isEdit ? '编辑文章' : '新建文章' }}</h1>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="editor-container">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">标题</label>
          <input
            type="text"
            id="title"
            v-model="title"
            class="form-control"
            required
          />
        </div>

        <div class="form-group">
          <label for="content">内容 (Markdown)</label>
          <textarea
            id="content"
            v-model="content"
            class="editor-textarea"
            required
            @input="updatePreview"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="excerpt">摘要</label>
          <textarea
            id="excerpt"
            v-model="excerpt"
            class="form-control"
            rows="3"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="category_id">分类</label>
            <select id="category_id" v-model="category_id" class="form-control">
              <option value="">请选择分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="status">状态</label>
            <select id="status" v-model="status" class="form-control">
              <option value="draft">草稿</option>
              <option value="published">发布</option>
              <option value="archived">归档</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '保存中...' : '保存' }}
          </button>
          <router-link to="/admin/articles" class="btn btn-secondary">取消</router-link>
        </div>
      </form>
    </div>

    <div class="preview-container" v-if="content">
      <h2>预览</h2>
      <div class="article-content" v-html="previewHtml"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { articlesApi } from '../api/articles';
import { categoriesApi } from '../api/categories';
import { marked } from 'marked';

export default {
  name: 'AdminArticleEdit',
  setup() {
    const title = ref('');
    const content = ref('');
    const excerpt = ref('');
    const category_id = ref('');
    const status = ref('draft');
    const categories = ref([]);
    const error = ref('');
    const loading = ref(false);

    const route = useRoute();
    const router = useRouter();
    const isEdit = computed(() => !!route.params.id);

    const previewHtml = computed(() => {
      return marked(content.value || '');
    });

    const updatePreview = () => {
      // 实时更新预览
    };

    const fetchCategories = async () => {
      try {
        const response = await categoriesApi.getList();
        categories.value = response.data.categories;
      } catch (e) {
        console.error('Failed to fetch categories:', e);
      }
    };

    const fetchArticle = async () => {
      if (!isEdit.value) return;

      try {
        const response = await articlesApi.getDetail(route.params.id);
        const article = response.data.article;
        title.value = article.title;
        content.value = article.content;
        excerpt.value = article.excerpt || '';
        category_id.value = article.category_id || '';
        status.value = article.status;
      } catch (e) {
        error.value = '获取文章失败';
      }
    };

    const handleSubmit = async () => {
      error.value = '';
      loading.value = true;

      try {
        const data = {
          title: title.value,
          content: content.value,
          excerpt: excerpt.value,
          category_id: category_id.value || null,
          status: status.value
        };

        if (isEdit.value) {
          await articlesApi.update(route.params.id, data);
        } else {
          await articlesApi.create(data);
        }

        router.push('/admin/articles');
      } catch (e) {
        error.value = e.response?.data?.error || '保存失败';
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchCategories();
      fetchArticle();
    });

    return {
      title,
      content,
      excerpt,
      category_id,
      status,
      categories,
      error,
      loading,
      isEdit,
      previewHtml,
      updatePreview,
      handleSubmit
    };
  }
};
</script>

<style scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
</style>
