<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue/es';
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import { articleApi, type ArticleCreate, type ArticleResponse, type Category, type Tag } from '@/api/article';

interface SelectOption {
  value: number;
  label: string;
  title: string;
}

interface CategoryWithDescription extends Category {
  description?: string;
}

interface TagWithDescription extends Tag {
  description?: string;
}

const form = reactive<ArticleCreate>({
  title: '',
  slug: '',
  content: '',
  summary: '',
  meta_title: '',
  meta_description: '',
  keywords: '',
  status: 'draft',
  is_featured: false,
  allow_comments: true,
  category_ids: [],
  tag_ids: []
});

const loading = ref(false);
const categories = ref<CategoryWithDescription[]>([]);
const tags = ref<TagWithDescription[]>([]);

const route = useRoute();
const router = useRouter();
const articleId = computed(() => route.params.id as string);
const isEdit = computed(() => !!articleId.value);

// 转换分类和标签为选项格式
const categoryOptions = computed<SelectOption[]>(() => 
  categories.value.map(c => ({ 
    value: c.id, 
    label: c.name,
    title: c.description || c.name
  }))
);

const tagOptions = computed<SelectOption[]>(() => 
  tags.value.map(t => ({ 
    value: t.id, 
    label: t.name,
    title: t.description || t.name
  }))
);

const filterOption = (input: string, option: SelectOption) => {
  return option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0;
};

// 加载分类和标签
const loadOptions = async () => {
  try {
    loading.value = true;
    const [categoriesRes, tagsRes] = await Promise.all([
      articleApi.getCategories(),
      articleApi.getTags()
    ]);
    
    if (!categoriesRes.data || !Array.isArray(categoriesRes.data.items)) {
      throw new Error('加载分类失败：无效的数据格式');
    }
    if (!tagsRes.data || !Array.isArray(tagsRes.data.items)) {
      throw new Error('加载标签失败：无效的数据格式');
    }
    
    categories.value = categoriesRes.data.items;
    tags.value = tagsRes.data.items;
  } catch (error) {
    message.error('加载分类和标签失败');
    console.error('加载分类和标签失败:', error);
  } finally {
    loading.value = false;
  }
};

// 加载文章数据
const loadArticle = async () => {
  if (!isEdit.value) return;
  
  try {
    loading.value = true;
    const response = await articleApi.get(parseInt(articleId.value));
    const article = response.data;
    
    // 更新表单数据
    Object.assign(form, {
      title: article.title,
      slug: article.slug,
      content: article.content,
      summary: article.summary || '',
      meta_title: article.meta_title || '',
      meta_description: article.meta_description || '',
      keywords: article.keywords || '',
      status: article.status,
      is_featured: article.is_featured,
      allow_comments: article.allow_comments,
      category_ids: article.categories.map(c => c.id),
      tag_ids: article.tags.map(t => t.id)
    });
  } catch (error) {
    message.error('加载文章数据失败');
  } finally {
    loading.value = false;
  }
};

// 提交表单
const handleSubmit = async () => {
  // 验证必填字段
  if (!form.title.trim()) {
    message.warning('请输入文章标题');
    return;
  }
  if (!form.slug.trim()) {
    message.warning('请输入文章别名');
    return;
  }
  if (!form.content.trim()) {
    message.warning('请输入文章内容');
    return;
  }
  if (!form.category_ids.length) {
    message.warning('请至少选择一个分类');
    return;
  }
  
  // 验证分类和标签的有效性
  const validCategoryIds = categories.value.map(c => c.id);
  const validTagIds = tags.value.map(t => t.id);
  
  const invalidCategories = form.category_ids.filter(id => !validCategoryIds.includes(id));
  if (invalidCategories.length > 0) {
    message.error('存在无效的分类选择');
    return;
  }
  
  const invalidTags = form.tag_ids.filter(id => !validTagIds.includes(id));
  if (invalidTags.length > 0) {
    message.error('存在无效的标签选择');
    return;
  }
  
  try {
    loading.value = true;
    if (isEdit.value) {
      const response = await articleApi.update(parseInt(articleId.value), form);
      if (response.code === 200) {
        message.success('文章更新成功');
        router.push('/admin/article');
      } else {
        throw new Error(response.message || '更新文章失败');
      }
    } else {
      const response = await articleApi.create(form);
      if (response.code === 201) {
        message.success('文章创建成功');
        router.push('/admin/article');
        // 只有在创建时才重置表单
        Object.assign(form, {
          title: '',
          slug: '',
          content: '',
          summary: '',
          meta_title: '',
          meta_description: '',
          keywords: '',
          status: 'draft',
          is_featured: false,
          allow_comments: true,
          category_ids: [],
          tag_ids: []
        });
      } else {
        throw new Error(response.message || '创建文章失败');
      }
    }
  } catch (error: any) {
    console.error('提交表单失败:', error);
    message.error(error.message || (isEdit.value ? '更新文章失败' : '创建文章失败'));
  } finally {
    loading.value = false;
  }
};

// 自动生成 slug
const generateSlug = (title: string) => {
  return title
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
};

const handleTitleChange = (e: Event) => {
  const title = (e.target as HTMLInputElement).value;
  if (!form.slug) {
    form.slug = generateSlug(title);
  }
};

// 处理图片上传
const handleUploadImages = async (files: FileList, callback: (urls: string[]) => void) => {
  try {
    const uploadPromises = Array.from(files).map(async (file) => {
      // 检查文件类型
      if (!file.type.startsWith('image/')) {
        throw new Error('只能上传图片文件');
      }
      
      // 检查文件大小（限制为 2MB）
      if (file.size > 2 * 1024 * 1024) {
        throw new Error('图片大小不能超过 2MB');
      }
      
      const formData = new FormData();
      formData.append('file', file);
      
      // 调用上传 API
      const response = await articleApi.uploadImage(formData);
      if (response.code === 200 && response.data?.url) {
        return response.data.url;
      } else {
        throw new Error('图片上传失败');
      }
    });
    
    const urls = await Promise.all(uploadPromises);
    callback(urls);
  } catch (error: any) {
    message.error(error.message || '图片上传失败');
  }
};

// 组件加载时获取分类和标签，以及文章数据（如果是编辑模式）
onMounted(async () => {
  await loadOptions();
  await loadArticle();
});
</script>

<template>
  <div class="article-edit">
    <a-form
      :model="form"
      layout="vertical"
      @finish="handleSubmit"
    >
      <a-form-item 
        label="标题" 
        required
        :rules="[{ required: true, message: '请输入文章标题' }]"
      >
        <a-input 
          v-model:value="form.title" 
          placeholder="请输入文章标题"
          @input="handleTitleChange"
        />
      </a-form-item>

      <a-form-item 
        label="别名" 
        required
        :rules="[{ required: true, message: '请输入文章别名' }]"
      >
        <a-input 
          v-model:value="form.slug" 
          placeholder="请输入文章别名，用于URL"
          :disabled="loading"
        />
      </a-form-item>

      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item 
            label="分类" 
            required
            :rules="[{ required: true, message: '请选择至少一个分类' }]"
          >
            <a-select
              v-model:value="form.category_ids"
              mode="multiple"
              placeholder="请选择分类"
              :options="categoryOptions"
              :loading="loading"
              show-search
              :filter-option="filterOption"
            >
              <template #option="{ label, title }">
                <a-tooltip :title="title">
                  <span>{{ label }}</span>
                </a-tooltip>
              </template>
            </a-select>
          </a-form-item>
        </a-col>
        
        <a-col :span="12">
          <a-form-item label="标签">
            <a-select
              v-model:value="form.tag_ids"
              mode="multiple"
              placeholder="请选择标签"
              :options="tagOptions"
              :loading="loading"
              show-search
              :filter-option="filterOption"
            >
              <template #option="{ label, title }">
                <a-tooltip :title="title">
                  <span>{{ label }}</span>
                </a-tooltip>
              </template>
            </a-select>
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item label="摘要">
        <a-textarea
          v-model:value="form.summary"
          placeholder="请输入文章摘要"
          :rows="4"
        />
      </a-form-item>

      <a-form-item label="内容" required>
        <md-editor
          v-model="form.content"
          :toolbars="[
            'bold',
            'underline',
            'italic',
            'strikeThrough',
            '-',
            'title',
            'sub',
            'sup',
            'quote',
            'unorderedList',
            'orderedList',
            '-',
            'link',
            'image',
            'table',
            'code',
            'codeRow',
            'preview',
            'fullscreen'
          ]"
          language="zh-CN"
          preview-theme="github"
          :preview="true"
          preview-only
          :style="{
            height: '600px'
          }"
          class="content-editor"
          @onUploadImg="handleUploadImages"
        />
      </a-form-item>

      <a-row :gutter="16">
        <a-col :span="8">
          <a-form-item label="状态">
            <a-select
              v-model:value="form.status"
              :options="[
                { value: 'draft', label: '草稿' },
                { value: 'published', label: '已发布' },
                { value: 'archived', label: '已归档' }
              ]"
            />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label=" ">
            <a-checkbox v-model:checked="form.is_featured">
              推荐文章
            </a-checkbox>
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label=" ">
            <a-checkbox v-model:checked="form.allow_comments">
              允许评论
            </a-checkbox>
          </a-form-item>
        </a-col>
      </a-row>

      <a-divider>SEO 设置</a-divider>

      <a-form-item label="Meta 标题">
        <a-input
          v-model:value="form.meta_title"
          placeholder="请输入 Meta 标题"
        />
      </a-form-item>

      <a-form-item label="Meta 描述">
        <a-textarea
          v-model:value="form.meta_description"
          placeholder="请输入 Meta 描述"
          :rows="2"
        />
      </a-form-item>

      <a-form-item label="关键词">
        <a-input
          v-model:value="form.keywords"
          placeholder="请输入关键词，多个关键词用英文逗号分隔"
        />
      </a-form-item>

      <div class="form-actions">
        <a-space>
          <a-button type="primary" html-type="submit" :loading="loading">
            {{ isEdit ? '保存' : '创建' }}
          </a-button>
          <a-button @click="$router.back()">取消</a-button>
        </a-space>
      </div>
    </a-form>
  </div>
</template>

<style lang="less" scoped>
.article-edit {
  padding: 24px;
  background: #fff;
  border-radius: 2px;
}

.edit-form {
  max-width: 1200px;
  margin: 0 auto;
}

.content-editor {
  :deep(.md-editor) {
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    
    &:hover {
      border-color: #40a9ff;
    }
    
    &-content {
      min-height: 400px;
    }
    
    &-preview {
      min-height: 400px;
      padding: 16px 24px;
      font-size: 16px;
      line-height: 1.6;
    }

    // 增大工具栏图标尺寸
    &-toolbar {
      .md-editor-toolbar-item {
        font-size: 20px;
        padding: 8px;
        
        svg {
          width: 20px;
          height: 20px;
        }
      }
    }
  }
}

:deep(.ant-form-item) {
  margin-bottom: 24px;
  
  &-label {
    font-weight: 500;
  }
}

:deep(.ant-input),
:deep(.ant-select-selector) {
  border-radius: 2px;
  
  &:hover {
    border-color: #40a9ff;
  }
  
  &:focus,
  &-focused {
    border-color: #40a9ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  }
}

.form-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}
</style> 