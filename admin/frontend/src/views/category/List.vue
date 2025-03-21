<template>
  <div class="category-list">
    <a-card title="分类管理" :bordered="false">
      <!-- 操作栏 -->
      <div class="operation-bar">
        <a-button type="primary" @click="showCreateModal">
          创建分类
        </a-button>
      </div>

      <!-- 分类列表 -->
      <a-table
        :columns="columns"
        :data-source="categories"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a @click="showEditModal(record)">编辑</a>
              <a-popconfirm
                title="确定要删除这个分类吗？"
                @confirm="handleDelete(record.id)"
              >
                <a class="danger">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 创建/编辑分类的模态框 -->
      <a-modal
        v-model:visible="modalVisible"
        :title="modalTitle"
        @ok="handleModalOk"
        @cancel="handleModalCancel"
      >
        <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          layout="vertical"
        >
          <a-form-item label="名称" name="name">
            <a-input v-model:value="formState.name" placeholder="请输入分类名称" />
          </a-form-item>
          <a-form-item label="描述" name="description">
            <a-textarea
              v-model:value="formState.description"
              placeholder="请输入分类描述"
              :rows="4"
            />
          </a-form-item>
        </a-form>
      </a-modal>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive } from 'vue'
import { message } from 'ant-design-vue/es'
import type { TablePaginationConfig } from 'ant-design-vue/es/table'
import { categoryApi } from '@/api/category'
import type { Category, CategoryCreate, CategoryUpdate, CategoryList } from '@/types/category'

// 表格列定义
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
    title: '描述',
    dataIndex: 'description',
    key: 'description',
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
  },
  {
    title: '操作',
    key: 'action',
  },
]

// 状态定义
const loading = ref(false)
const categories = ref<Category[]>([])
const pagination = reactive<Partial<TablePaginationConfig>>({
  total: 0,
  current: 1,
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`,
})

// 模态框状态
const modalVisible = ref(false)
const modalTitle = ref('创建分类')
const formRef = ref()
const formState = reactive<CategoryCreate>({
  name: '',
  description: '',
})
const editingId = ref<number | null>(null)

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应在 2 到 50 个字符之间', trigger: 'blur' },
  ],
}

// 加载分类列表
const loadCategories = async () => {
  loading.value = true
  try {
    const response = await categoryApi.list({ 
      page: pagination.current, 
      page_size: pagination.pageSize 
    })
    if (response.code === 200) {
      categories.value = response.data.items
      pagination.total = response.data.total
    }
  } catch (error) {
    message.error('加载分类列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 表格分页变化处理
const handleTableChange = (pag: TablePaginationConfig) => {
  if (pag) {
    pagination.current = pag.current || 1
    pagination.pageSize = pag.pageSize || 10
    loadCategories()
  }
}

// 显示创建模态框
const showCreateModal = () => {
  editingId.value = null
  modalTitle.value = '创建分类'
  formState.name = ''
  formState.description = ''
  modalVisible.value = true
}

// 显示编辑模态框
const showEditModal = (record: Category) => {
  editingId.value = record.id
  modalTitle.value = '编辑分类'
  formState.name = record.name
  formState.description = record.description || ''
  modalVisible.value = true
}

// 处理模态框确认
const handleModalOk = async () => {
  try {
    await formRef.value.validate()
    if (editingId.value === null) {
      // 创建分类
      await categoryApi.create(formState)
      message.success('创建分类成功')
    } else {
      // 更新分类
      await categoryApi.update(editingId.value, formState)
      message.success('更新分类成功')
    }
    modalVisible.value = false
    loadCategories()
  } catch (error) {
    console.error(error)
  }
}

// 处理模态框取消
const handleModalCancel = () => {
  modalVisible.value = false
  formRef.value?.resetFields()
}

// 处理删除分类
const handleDelete = async (id: number) => {
  try {
    await categoryApi.delete(id)
    message.success('删除分类成功')
    loadCategories()
  } catch (error) {
    message.error('删除分类失败')
    console.error(error)
  }
}

// 页面加载时获取分类列表
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.category-list {
  padding: 24px;
}

.operation-bar {
  margin-bottom: 16px;
}

.danger {
  color: #ff4d4f;
}
</style> 