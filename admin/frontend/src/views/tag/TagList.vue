<template>
  <div class="tag-list">
    <a-card title="标签管理">
      <template #extra>
        <a-button type="primary" @click="showModal()">
          新建标签
        </a-button>
      </template>

      <!-- 标签列表表格 -->
      <a-table
        :columns="columns"
        :data-source="tags"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" @click="showModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除这个标签吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 新建/编辑标签对话框 -->
      <a-modal
        v-model:visible="modalVisible"
        :title="editingTag ? '编辑标签' : '新建标签'"
        @ok="handleSubmit"
        @cancel="handleCancel"
      >
        <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          layout="vertical"
        >
          <a-form-item label="名称" name="name">
            <a-input v-model:value="formState.name" placeholder="请输入标签名称" />
          </a-form-item>
          <a-form-item label="别名" name="slug">
            <a-input v-model:value="formState.slug" placeholder="可选，留空将自动生成" />
          </a-form-item>
          <a-form-item label="描述" name="description">
            <a-textarea
              v-model:value="formState.description"
              placeholder="请输入标签描述"
              :rows="4"
            />
          </a-form-item>
        </a-form>
      </a-modal>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import message from 'ant-design-vue/es/message';
import type { TablePaginationConfig } from 'ant-design-vue/es/table';
import { tagApi } from '@/api/tag';
import type { Tag } from '@/api/tag';

// 定义表格列
const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
  },
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '别名',
    dataIndex: 'slug',
    key: 'slug',
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
  },
];

// 状态定义
const loading = ref(false);
const tags = ref<Tag[]>([]);
const modalVisible = ref(false);
const editingTag = ref<Tag | null>(null);
const formRef = ref();

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
});

// 表单状态
const formState = reactive({
  name: '',
  slug: '',
  description: '',
});

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
};

// 加载标签列表
const loadTags = async () => {
  loading.value = true;
  try {
    const response = await tagApi.list({ page: pagination.current, size: pagination.pageSize });
    if (response.code === 200) {
      tags.value = response.data.items;
      pagination.total = response.data.total;
    }
  } catch (error) {
    message.error('加载标签失败');
  } finally {
    loading.value = false;
  }
};

// 处理表格变化
const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.current = pag.current || 1;
  pagination.pageSize = pag.pageSize || 10;
  loadTags();
};

// 显示模态框
const showModal = (tag?: any) => {
  if (tag) {
    editingTag.value = tag;
    Object.assign(formState, tag);
  } else {
    editingTag.value = null;
    Object.assign(formState, { name: '', slug: '', description: '' });
  }
  modalVisible.value = true;
};

// 处理表单提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    if (editingTag.value) {
      const response = await tagApi.update(editingTag.value.id, formState);
      if (response.code === 200) {
        message.success('标签更新成功');
      }
    } else {
      const response = await tagApi.create(formState);
      if (response.code === 201) {
        message.success('标签创建成功');
      }
    }
    modalVisible.value = false;
    loadTags();
  } catch (error) {
    console.error('表单验证失败:', error);
  }
};

// 处理取消
const handleCancel = () => {
  modalVisible.value = false;
  formRef.value?.resetFields();
};

// 处理删除
const handleDelete = async (id: number) => {
  try {
    const response = await tagApi.delete(id);
    if (response.code === 200) {
      message.success('标签删除成功');
      loadTags();
    }
  } catch (error) {
    message.error('删除标签失败');
  }
};

// 页面加载时获取标签列表
onMounted(() => {
  loadTags();
});
</script>

<style scoped>
.tag-list {
  padding: 24px;
}
</style>