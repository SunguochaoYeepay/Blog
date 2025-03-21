<template>
  <div class="user-list">
    <!-- 搜索区域 -->
    <a-card class="search-card" :bordered="false">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="用户名">
          <a-input
            v-model:value="searchForm.username"
            placeholder="请输入用户名"
            allow-clear
            @pressEnter="handleSearch"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item label="邮箱">
          <a-input
            v-model:value="searchForm.email"
            placeholder="请输入邮箱"
            allow-clear
            @pressEnter="handleSearch"
          >
            <template #prefix>
              <MailOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item label="角色">
          <a-select
            v-model:value="searchForm.role"
            placeholder="请选择角色"
            style="width: 120px"
            allow-clear
          >
            <a-select-option v-for="option in roleOptions" :key="option.value" :value="option.value">
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
      <template #title>
        <div class="table-toolbar">
          <div class="toolbar-title">
            用户列表
            <a-tag v-if="total" color="blue">{{ total }} 人</a-tag>
          </div>
          <div class="toolbar-buttons">
            <a-space>
              <a-button type="primary" @click="handleCreate">
                <template #icon><UserAddOutlined /></template>
                创建用户
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
        :data-source="users"
        :loading="loading"
        :pagination="pagination"
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        :row-key="(record: TableUser) => record.id"
        @change="handleTableChange"
      >
        <!-- 用户名列 -->
        <template #username="{ record }">
          <div class="user-cell">
            <div class="avatar-wrapper">
              <a-avatar 
                :src="record.avatar"
                :style="{ backgroundColor: !record.avatar ? getAvatarColor(record.username) : 'transparent' }"
                :size="40"
              >
                {{ !record.avatar ? record.username.charAt(0).toUpperCase() : '' }}
              </a-avatar>
            </div>
            <div class="user-info">
              <div class="username">{{ record.username }}</div>
              <div class="email">{{ record.email }}</div>
              <div class="full-name">{{ record.full_name }}</div>
            </div>
          </div>
        </template>

        <!-- 文章数列 -->
        <template #articles_count="{ text }">
          <a-badge 
            :count="Number(text)" 
            :number-style="{ backgroundColor: Number(text) > 0 ? '#52c41a' : '#d9d9d9' }" 
          />
        </template>

        <!-- 评论数列 -->
        <template #comments_count="{ text }">
          <a-badge 
            :count="Number(text)" 
            :number-style="{ backgroundColor: Number(text) > 0 ? '#52c41a' : '#d9d9d9' }" 
          />
        </template>

        <!-- 角色列 -->
        <template #role="{ text }">
          <a-tag :color="getRoleTagColor(text)">
            {{ getRoleLabel(text) }}
          </a-tag>
        </template>

        <!-- 状态列 -->
        <template #status="{ text }">
          <a-tag :color="text === 'active' ? 'success' : 'error'">
            {{ text === 'active' ? '活跃' : '禁用' }}
          </a-tag>
        </template>

        <!-- 最后登录列 -->
        <template #last_login="{ text }">
          <span :title="text ? new Date(text).toLocaleString() : '从未登录'">
            {{ formatLastLoginDate(text) }}
          </span>
        </template>

        <!-- 操作列 -->
        <template #action="{ record }">
          <a-space>
            <a-button type="link" size="small" @click="handleEdit(record.id)">
              <template #icon><EditOutlined /></template>
              编辑
            </a-button>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除此用户吗？"
              @confirm="handleDelete(record.id)"
              ok-text="确定"
              cancel-text="取消"
            >
              <a-button type="link" danger size="small">
                <template #icon><DeleteOutlined /></template>
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue/es';
import type { UploadChangeParam, UploadFile } from 'ant-design-vue/es/upload';
import type { TableProps } from 'ant-design-vue/es/table';
import { 
  UserOutlined,
  MailOutlined,
  TeamOutlined,
  SearchOutlined,
  ReloadOutlined,
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined
} from '@ant-design/icons-vue';
import userApi from '@/api/user';
import type { User } from '@/api/user';
import { formatDate } from '@/utils/date';

interface TableUser extends User {
  articles_count: number;
  comments_count: number;
}

const router = useRouter();
const loading = ref(false);
const users = ref<TableUser[]>([]);
const total = ref(0);
const selectedRowKeys = ref<number[]>([]);
const searchForm = ref({
  username: '',
  email: '',
  role: undefined as string | undefined,
});

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: (total: number) => `共 ${total} 条记录`,
  showSizeChanger: true,
  showQuickJumper: true,
});

// 角色选项
const roleOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'editor', label: '编辑' },
  { value: 'user', label: '普通用户' }
];

// 表格列定义
const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    width: '20%',
    slots: {
      customRender: 'username'
    }
  },
  {
    title: '部门',
    dataIndex: 'department',
    width: '12%'
  },
  {
    title: '文章数',
    dataIndex: 'articles_count',
    width: '8%',
    sorter: true,
    slots: {
      customRender: 'articles_count'
    }
  },
  {
    title: '评论数',
    dataIndex: 'comments_count',
    width: '8%',
    sorter: true,
    slots: {
      customRender: 'comments_count'
    }
  },
  {
    title: '角色',
    dataIndex: 'role',
    width: '10%',
    filters: [
      { text: '管理员', value: 'admin' },
      { text: '编辑', value: 'editor' },
      { text: '用户', value: 'user' }
    ],
    slots: {
      customRender: 'role'
    }
  },
  {
    title: '状态',
    dataIndex: 'status',
    width: '8%',
    filters: [
      { text: '活跃', value: 'active' },
      { text: '禁用', value: 'inactive' }
    ],
    slots: {
      customRender: 'status'
    }
  },
  {
    title: '最后登录',
    dataIndex: 'last_login',
    width: '15%',
    sorter: true,
    slots: {
      customRender: 'last_login'
    }
  },
  {
    title: '操作',
    key: 'action',
    width: '15%',
    slots: {
      customRender: 'action'
    }
  }
];

// 加载用户列表
const loadUsers = async () => {
  try {
    loading.value = true;
    const page = pagination.value.current || 1;
    const pageSize = pagination.value.pageSize || 10;
    const response = await userApi.list({
      page,
      page_size: pageSize,
      username: searchForm.value.username,
      email: searchForm.value.email,
      role: searchForm.value.role
    });
    users.value = response.data.items.map(user => ({
      ...user,
      articles_count: user.articles_count || 0,
      comments_count: user.comments_count || 0
    }));
    total.value = response.data.total;
    pagination.value.total = response.data.total;
  } catch (error) {
    console.error('加载用户列表失败:', error);
    message.error('加载用户列表失败');
  } finally {
    loading.value = false;
  }
};

// 处理搜索
const handleSearch = () => {
  pagination.value.current = 1;
  loadUsers();
};

// 处理重置
const handleReset = () => {
  searchForm.value = {
    username: '',
    email: '',
    role: undefined,
  };
  pagination.value.current = 1;
  loadUsers();
};

// 处理表格变化
const handleTableChange: TableProps['onChange'] = (pag, filters, sorter) => {
  pagination.value.current = pag?.current || 1;
  pagination.value.pageSize = pag?.pageSize || 10;
  
  if (filters?.role?.length) {
    searchForm.value.role = filters.role[0] as string;
  } else {
    searchForm.value.role = undefined;
  }
  
  loadUsers();
};

// 处理选择变化
const onSelectChange = (selectedKeys: number[]) => {
  selectedRowKeys.value = selectedKeys;
};

// 处理创建
const handleCreate = () => {
  router.push('/admin/user/create');
};

// 处理编辑
const handleEdit = (id: number) => {
  router.push(`/admin/user/edit/${id}`);
};

// 处理删除
const handleDelete = (id: number) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个用户吗？',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await userApi.delete(id);
        message.success('删除成功');
        loadUsers();
      } catch (error) {
        message.error('删除失败');
      }
    },
  });
};

// 处理批量删除
const handleBatchDelete = () => {
  if (!selectedRowKeys.value.length) {
    message.warning('请选择要删除的用户');
    return;
  }

  Modal.confirm({
    title: '确认删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个用户吗？`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await userApi.batchDelete(selectedRowKeys.value);
        message.success('批量删除成功');
        selectedRowKeys.value = [];
        loadUsers();
      } catch (error) {
        message.error('批量删除失败');
      }
    },
  });
};

// 工具函数
const getRoleTagColor = (role: string) => {
  const colorMap: Record<string, string> = {
    admin: 'red',
    editor: 'green',
    user: 'blue',
  };
  return colorMap[role] || 'default';
};

const getRoleLabel = (role: string) => {
  const option = roleOptions.find(opt => opt.value === role);
  return option ? option.label : role;
};

const getUserStatus = (user: TableUser) => {
  const lastLogin = user.last_login ? new Date(user.last_login) : null;
  const now = new Date();
  
  if (!lastLogin) {
    return { status: 'default', text: '未登录' };
  }
  
  const diff = now.getTime() - lastLogin.getTime();
  if (diff < 30 * 60 * 1000) { // 30分钟内
    return { status: 'success', text: '在线' };
  } else if (diff < 24 * 60 * 60 * 1000) { // 24小时内
    return { status: 'warning', text: '离线' };
  } else {
    return { status: 'default', text: '长期未登录' };
  }
};

const getAvatarColor = (username: string) => {
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae'];
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

const formatLastLoginDate = (dateStr: string | null) => {
  if (!dateStr) return '从未登录';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    if (hours < 1) {
      const minutes = Math.floor(diff / (60 * 1000));
      return `${minutes} 分钟前`;
    }
    return `${hours} 小时前`;
  }
  
  return date.toLocaleString();
};

onMounted(() => {
  loadUsers();
});
</script>

<style lang="less" scoped>
.user-list {
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

  .user-cell {
    display: flex;
    align-items: center;
    gap: 12px;

    .avatar-wrapper {
      position: relative;
      cursor: pointer;
      
      &:hover .avatar-edit-overlay {
        opacity: 1;
      }

      .avatar-edit-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;
        color: white;
      }
    }

    .user-info {
      .username {
        font-weight: 500;
        line-height: 1.5715;
      }

      .email {
        font-size: 12px;
        color: rgba(0, 0, 0, 0.45);
        line-height: 1.5715;
      }
    }
  }

  .avatar-upload {
    text-align: center;

    .avatar-preview {
      width: 200px;
      height: 200px;
      margin: 0 auto 20px;
      border: 1px dashed #d9d9d9;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #fafafa;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .avatar-placeholder {
        color: #999;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
      }
    }

    .upload-actions {
      display: flex;
      justify-content: center;
      gap: 8px;
      margin-bottom: 16px;
    }

    .upload-tips {
      color: #999;
      font-size: 12px;
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