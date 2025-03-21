<template>
  <div class="article-list">
    <!-- 搜索区域 -->
    <a-card class="search-card" :bordered="false">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="文章标题">
          <a-input
            v-model:value="searchForm.title"
            placeholder="请输入文章标题"
            allow-clear
            @pressEnter="handleSearch"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            style="width: 120px"
            allow-clear
          >
            <a-select-option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" @click="handleSearch">
              <template #icon><SearchOutlined /></template>
              搜索
            </a-button>
            <a-button @click="handleReset">
              <template #icon><ReloadOutlined /></template>
              重置
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 表格区域 -->
    <a-card class="table-card" :bordered="false">
      <!-- 表格工具栏 -->
      <template #title>
        <div class="table-toolbar">
          <div class="toolbar-title">
            文章列表
            <a-tag v-if="pagination.total" color="blue">{{ pagination.total }} 篇</a-tag>
          </div>
          <div class="toolbar-buttons">
            <a-space>
              <a-button type="primary" @click="handleCreate">
                <template #icon><PlusOutlined /></template>
                创建文章
              </a-button>
              <a-button 
                danger 
                :disabled="!selectedRowKeys.length"
                @click="handleBatchDelete"
              >
                <template #icon><DeleteOutlined /></template>
                批量删除
              </a-button>
            </a-space>
          </div>
        </div>
      </template>

      <a-table
        :columns="columns"
        :data-source="articles"
        :loading="loading"
        :pagination="pagination"
        :row-selection="{ 
          selectedRowKeys, 
          onChange: (keys: number[]) => selectedRowKeys = keys 
        }"
        :row-key="(record: ArticleResponse) => record.id"
        @change="handleTableChange"
      >
        <!-- 标题列 -->
        <template #bodyCell="{ column, record, text }">
          <template v-if="column.key === 'title'">
            <a @click="handleEdit(record.id)">{{ text }}</a>
          </template>
          <!-- 状态列 -->
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusConfig(text).color">
              {{ getStatusConfig(text).text }}
            </a-tag>
          </template>
          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" @click="handleEdit(record.id)">编辑</a-button>
              <a-divider type="vertical" />
              <a-button type="link" danger @click="handleDelete(record.id)">删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  PlusOutlined, 
  SearchOutlined, 
  DeleteOutlined, 
  ReloadOutlined 
} from '@ant-design/icons-vue';
import Modal from 'ant-design-vue/es/modal';
import message from 'ant-design-vue/es/message';
import { articleApi, type ArticleResponse } from '@/api/article';
import type { TableProps } from 'ant-design-vue/es/table';
import type { ColumnsType, SorterResult, TablePaginationConfig } from 'ant-design-vue/es/table/interface';

const router = useRouter();
const loading = ref(false);
const articles = ref<ArticleResponse[]>([]);
const selectedRowKeys = ref<number[]>([]);
const searchForm = ref({
  title: '',
  status: undefined as 'draft' | 'published' | 'archived' | undefined,
});

const pagination = ref<TablePaginationConfig>({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: (total: number) => `共 ${total} 条记录`,
  showSizeChanger: true,
  showQuickJumper: true,
});

// 排序状态
const sortState = ref({
  field: undefined as string | undefined,
  order: undefined as 'ascend' | 'descend' | undefined,
});

// 状态选项
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'published', label: '已发布' },
  { value: 'archived', label: '已归档' },
];

// 表格列定义
const columns: ColumnsType<ArticleResponse> = [
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    width: '30%',
    sorter: true,
    ellipsis: true,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '12%',
    filters: statusOptions.map(option => ({
      text: option.label,
      value: option.value
    })),
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: '20%',
    sorter: true,
    customRender: ({ text }) => formatDate(text)
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    key: 'updated_at',
    width: '20%',
    sorter: true,
    customRender: ({ text }) => formatDate(text)
  },
  {
    title: '操作',
    key: 'action',
    width: '18%',
    fixed: 'right'
  }
];

// 加载文章列表
const loadArticles = async () => {
  try {
    loading.value = true;
    const page = pagination.value.current || 1;
    const page_size = pagination.value.pageSize || 10;
    const response = await articleApi.list({
      page,
      page_size,
      title: searchForm.value.title,
      status: searchForm.value.status,
      sort_field: sortState.value.field,
      sort_order: sortState.value.order,
    });
    articles.value = response.data.items;
    pagination.value.total = response.data.total;
  } catch (error) {
    console.error('加载文章列表失败:', error);
    articles.value = [];
    pagination.value.total = 0;
    message.error('加载文章列表失败');
  } finally {
    loading.value = false;
  }
};

// 处理搜索
const handleSearch = () => {
  pagination.value.current = 1;
  loadArticles();
};

// 重置搜索
const handleReset = () => {
  searchForm.value = {
    title: '',
    status: undefined,
  };
  sortState.value = {
    field: undefined,
    order: undefined,
  };
  pagination.value.current = 1;
  loadArticles();
};

// 处理表格变化
const handleTableChange: TableProps['onChange'] = (
  pag,
  filters,
  sorter
) => {
  // 处理分页
  if (pag) {
    pagination.value.current = pag.current || 1;
    pagination.value.pageSize = pag.pageSize || 10;
  }
  
  // 处理排序
  if (sorter && !Array.isArray(sorter) && 'field' in sorter) {
    sortState.value.field = sorter.field as string;
    sortState.value.order = sorter.order === 'ascend' ? 'ascend' : sorter.order === 'descend' ? 'descend' : undefined;
  } else {
    sortState.value.field = undefined;
    sortState.value.order = undefined;
  }

  // 处理筛选
  if (filters?.status?.length) {
    const [status] = filters.status;
    searchForm.value.status = status as typeof searchForm.value.status;
  } else {
    searchForm.value.status = undefined;
  }
  
  loadArticles();
};

// 跳转到创建文章页面
const handleCreate = () => {
  router.push('/admin/article/create');
};

// 编辑文章
const handleEdit = (id: number | undefined) => {
  if (typeof id === 'number') {
    router.push(`/admin/article/edit/${id}`);
  }
};

// 删除文章
const handleDelete = (id: number | undefined) => {
  if (typeof id !== 'number') return;
  
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这篇文章吗？',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await articleApi.delete(id);
        message.success('删除成功');
        loadArticles();
      } catch (error) {
        message.error('删除失败');
      }
    },
  });
};

// 批量删除文章
const handleBatchDelete = () => {
  if (!selectedRowKeys.value.length) {
    message.warning('请选择要删除的文章');
    return;
  }

  Modal.confirm({
    title: '确认删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 篇文章吗？`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await Promise.all(selectedRowKeys.value.map(id => articleApi.delete(id)));
        message.success('批量删除成功');
        selectedRowKeys.value = [];
        loadArticles();
      } catch (error) {
        message.error('批量删除失败');
      }
    },
  });
};

// 获取状态标签配置
const getStatusConfig = (status: string) => {
  const statusMap = {
    draft: { text: '草稿', color: 'orange' },
    published: { text: '已发布', color: 'green' },
    archived: { text: '已归档', color: 'red' },
  };
  return statusMap[status as keyof typeof statusMap] || { text: status || '未知', color: 'default' };
};

// 格式化时间
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  loadArticles();
});
</script>

<style lang="less" scoped>
.article-list {
  .search-card {
    margin-bottom: 16px;
    
    :deep(.ant-card-body) {
      padding: 24px;
    }

    .ant-form {
      .ant-form-item {
        margin-bottom: 0;
        margin-right: 16px;
      }
    }
  }

  .table-card {
    :deep(.ant-card-body) {
      padding: 0;
    }

    :deep(.ant-table-wrapper) {
      .ant-table-pagination {
        margin: 16px;
      }
    }
  }

  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #f0f0f0;

    .toolbar-title {
      font-size: 16px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  :deep(.ant-table) {
    .ant-table-cell {
      .ant-tag {
        margin-right: 0;
      }
    }
  }

  // 响应式调整
  @media screen and (max-width: 768px) {
    .search-card {
      :deep(.ant-form) {
        .ant-form-item {
          margin-bottom: 16px;
          margin-right: 0;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }

    .table-toolbar {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;

      .toolbar-buttons {
        width: 100%;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}
</style>