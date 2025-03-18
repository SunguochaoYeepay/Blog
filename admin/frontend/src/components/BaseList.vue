# 基础列表页面组件
<template>
  <div class="base-list">
    <!-- 搜索区域 -->
    <a-card class="search-form" :bordered="false">
      <a-form layout="inline" :model="searchForm">
        <slot name="search-form"></slot>
        <a-form-item class="search-buttons">
          <a-space>
            <a-button type="primary" @click="handleSearch">
              搜索
            </a-button>
            <a-button @click="handleReset">
              重置
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 操作区域 -->
    <a-card 
      v-if="$slots['table-operations']" 
      class="table-operations" 
      :bordered="false"
    >
      <slot name="table-operations"></slot>
    </a-card>

    <!-- 数据表格 -->
    <a-card class="data-table" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        :row-key="rowKey"
      >
        <template #bodyCell="{ column, record }">
          <slot name="column-content" :column="column" :record="record"></slot>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TablePaginationConfig } from 'ant-design-vue/es/table/interface'

interface Props {
  columns: any[]
  dataSource: any[]
  loading?: boolean
  pagination?: TablePaginationConfig
  searchForm?: any
  rowKey?: string | ((record: any) => string)
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  rowKey: 'id',
  pagination: () => ({
    total: 0,
    current: 1,
    pageSize: 10,
    showSizeChanger: true,
    showQuickJumper: true
  })
})

const emit = defineEmits<{
  (e: 'search'): void
  (e: 'reset'): void
  (e: 'table-change', pagination: TablePaginationConfig): void
}>()

const handleSearch = () => {
  emit('search')
}

const handleReset = () => {
  emit('reset')
}

const handleTableChange = (pag: TablePaginationConfig) => {
  emit('table-change', pag)
}
</script>

<style scoped>
.base-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 16px;
}

.search-form :deep(.ant-form) {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.search-form :deep(.search-buttons) {
  margin-left: auto;
}

.table-operations {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-table {
  margin-bottom: 24px;
}

/* 统一表格样式 */
.data-table :deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 500;
}

.data-table :deep(.ant-table-tbody > tr > td) {
  padding: 12px 8px;
}

/* 操作列样式 */
.data-table :deep(.operation-column) {
  .ant-space {
    gap: 8px;
  }
}
</style> 