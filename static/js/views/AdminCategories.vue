/**
 * 后台分类管理组件
 */
<template>
  <div class="admin-categories">
    <div class="admin-header">
      <h1>分类管理</h1>
      <button @click="showModal = true" class="btn btn-primary">新建分类</button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="success" class="success-message">{{ success }}</div>

    <div class="data-table">
      <table v-if="categories.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>Slug</th>
            <th>描述</th>
            <th>文章数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>{{ cat.id }}</td>
            <td>{{ cat.name }}</td>
            <td>{{ cat.slug }}</td>
            <td>{{ cat.description || '-' }}</td>
            <td>-</td>
            <td class="table-actions">
              <button @click="editCategory(cat)" class="btn btn-secondary btn-small">编辑</button>
              <button @click="deleteCategory(cat)" class="btn btn-danger btn-small">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">暂无分类</p>
    </div>

    <!-- 分类弹窗 -->
    <div class="modal" v-if="showModal">
      <div class="modal-content">
        <h3>{{ editingCategory ? '编辑分类' : '新建分类' }}</h3>
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label for="name">名称</label>
            <input
              type="text"
              id="name"
              v-model="formData.name"
              class="form-control"
              required
            />
          </div>
          <div class="form-group">
            <label for="slug">Slug</label>
            <input
              type="text"
              id="slug"
              v-model="formData.slug"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="description">描述</label>
            <textarea
              id="description"
              v-model="formData.description"
              class="form-control"
              rows="3"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '保存中...' : '保存' }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { categoriesApi } from '../api/categories';

export default {
  name: 'AdminCategories',
  setup() {
    const categories = ref([]);
    const showModal = ref(false);
    const editingCategory = ref(null);
    const error = ref('');
    const success = ref('');
    const loading = ref(false);

    const formData = ref({
      name: '',
      slug: '',
      description: ''
    });

    const fetchCategories = async () => {
      try {
        const response = await categoriesApi.getList();
        categories.value = response.data.categories;
      } catch (e) {
        console.error('Failed to fetch categories:', e);
      }
    };

    const editCategory = (cat) => {
      editingCategory.value = cat;
      formData.value = { name: cat.name, slug: cat.slug, description: cat.description || '' };
      showModal.value = true;
    };

    const deleteCategory = async (cat) => {
      if (!confirm(`确定要删除分类 "${cat.name}" 吗？`)) return;

      try {
        await categoriesApi.delete(cat.id);
        success.value = '删除成功';
        fetchCategories();
      } catch (e) {
        error.value = e.response?.data?.error || '删除失败';
      }
    };

    const saveCategory = async () => {
      error.value = '';
      success.value = '';
      loading.value = true;

      try {
        if (editingCategory.value) {
          await categoriesApi.update(editingCategory.value.id, formData.value);
          success.value = '更新成功';
        } else {
          await categoriesApi.create(formData.value);
          success.value = '创建成功';
        }
        closeModal();
        fetchCategories();
      } catch (e) {
        error.value = e.response?.data?.error || '保存失败';
      } finally {
        loading.value = false;
      }
    };

    const closeModal = () => {
      showModal.value = false;
      editingCategory.value = null;
      formData.value = { name: '', slug: '', description: '' };
    };

    onMounted(() => {
      fetchCategories();
    });

    return {
      categories,
      showModal,
      editingCategory,
      formData,
      error,
      success,
      loading,
      editCategory,
      deleteCategory,
      saveCategory,
      closeModal
    };
  }
};
</script>

<style scoped>
.no-data {
  text-align: center;
  padding: 30px;
  color: var(--text-light);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--white);
  border-radius: var(--radius);
  padding: 30px;
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
</style>
