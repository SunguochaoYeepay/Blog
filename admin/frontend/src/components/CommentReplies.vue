<template>
  <div v-if="replies && replies.length > 0" class="replies">
    <a-table
      :data-source="replies"
      :columns="columns"
      :pagination="false"
      size="small"
      :show-header="false"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'content'">
          <div class="reply-content-wrapper">
            <div class="reply-header">
              <div class="reply-user-info">
                <a-avatar :size="24" class="reply-avatar">
                  {{ record.user_name?.[0]?.toUpperCase() }}
                </a-avatar>
                <span class="reply-user">{{ record.user_name }}</span>
                <a-tag :color="getStatusColor(record)" class="reply-status-tag">
                  {{ getStatusText(record) }}
                </a-tag>
              </div>
              <span class="reply-time">{{ formatDate(record.created_at) }}</span>
            </div>
            <div class="reply-content">{{ record.content }}</div>
            <div class="reply-footer">
              <a-space>
                <a-button type="link" size="small" @click="$emit('view', record)">
                  查看
                </a-button>
                <a-button
                  v-if="!record.is_approved && !record.is_spam"
                  type="link"
                  size="small"
                  @click="$emit('approve', record)"
                >
                  通过
                </a-button>
                <a-button
                  v-if="!record.is_spam"
                  type="link"
                  size="small"
                  danger
                  @click="$emit('mark-spam', record)"
                >
                  标记垃圾
                </a-button>
                <a-popconfirm
                  title="确定要删除这条回复吗？"
                  @confirm="$emit('delete', record)"
                  ok-text="确定"
                  cancel-text="取消"
                >
                  <a-button type="link" size="small" danger>删除</a-button>
                </a-popconfirm>
              </a-space>
            </div>
          </div>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import dayjs from 'dayjs'
import type { CommentResponse } from '@/types/comment'

// 定义属性
const props = defineProps<{
  replies: CommentResponse[]
}>()

// 定义事件
defineEmits<{
  (e: 'view', reply: CommentResponse): void
  (e: 'approve', reply: CommentResponse): void
  (e: 'mark-spam', reply: CommentResponse): void
  (e: 'delete', reply: CommentResponse): void
}>()

// 表格列定义
const columns = [
  {
    dataIndex: 'content',
    key: 'content',
    width: '100%'
  }
]

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取状态文本
const getStatusText = (reply: CommentResponse) => {
  if (reply.is_spam) return '垃圾'
  if (reply.is_approved) return '已通过'
  return '待审核'
}

// 获取状态颜色
const getStatusColor = (reply: CommentResponse) => {
  if (reply.is_spam) return 'red'
  if (reply.is_approved) return 'green'
  return 'orange'
}
</script>

<style scoped>
.replies {
  margin: 8px 0;
  background: #fafafa;
  border-radius: 4px;
}

.replies :deep(.ant-table) {
  background: transparent;
}

.replies :deep(.ant-table-tbody > tr > td) {
  border-bottom: none;
  padding: 12px 16px;
}

.replies :deep(.ant-table-tbody > tr:hover > td) {
  background: #f0f0f0;
}

.reply-content-wrapper {
  width: 100%;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reply-user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-avatar {
  background: #1890ff;
}

.reply-user {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.reply-status-tag {
  margin-left: 8px;
}

.reply-time {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.reply-content {
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 12px;
  line-height: 1.5;
}

.reply-footer {
  display: flex;
  justify-content: flex-end;
}

.reply-footer :deep(.ant-btn) {
  padding: 0 4px;
}
</style>