<template>
  <base-list
    :columns="columns"
    :data-source="commentList"
    :loading="loading"
    :pagination="pagination"
    :search-form="searchForm"
    @search="handleSearch"
    @reset="handleReset"
    @table-change="handleTableChange"
  >
    <!-- 搜索表单 -->
    <template #search-form>
      <a-form-item label="评论内容">
        <a-input
          v-model:value="searchForm.keyword"
          placeholder="评论内容"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="文章标题">
        <a-input
          v-model:value="searchForm.article_title"
          placeholder="文章标题"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="状态">
        <a-select
          v-model:value="searchForm.status"
          style="width: 120px"
          :options="COMMENT_STATUS_OPTIONS"
        />
      </a-form-item>
      <a-form-item label="时间范围">
        <a-range-picker
          v-model:value="dateRange"
          @change="onDateRangeChange"
        />
      </a-form-item>
      <a-form-item label="显示方式">
        <a-radio-group v-model:value="searchForm.only_root">
          <a-radio :value="false">全部评论</a-radio>
          <a-radio :value="true">仅显示主评论</a-radio>
        </a-radio-group>
      </a-form-item>
    </template>

    <!-- 表格列内容 -->
    <template #column-content="{ column, record }">
      <template v-if="column.key === 'content'">
        <div>
          <div class="comment-content" @click="handleViewDetail(record)">
            {{ record.content }}
          </div>
          <div v-if="record.reply_count > 0" class="reply-info">
            <a-button type="link" @click="showReplies(record)">
              <template #icon><MessageOutlined /></template>
              {{ record.reply_count }} 条回复
            </a-button>
          </div>
          <div v-if="record.parent_id" class="reply-to">
            <small>回复评论 #{{ record.parent_id }}</small>
          </div>
        </div>
      </template>

      <template v-if="column.key === 'status'">
        <a-tag :color="getStatusColor(record)">
          {{ getStatusText(record) }}
        </a-tag>
      </template>

      <template v-if="column.key === 'action'">
        <div class="action-column">
          <a-space>
            <a-button
              v-if="!record.is_approved && !record.is_spam"
              type="link"
              @click="() => handleApprove(record)"
            >
              通过
            </a-button>
            <a-button
              v-if="!record.is_spam"
              type="link"
              danger
              @click="() => handleMarkSpam(record)"
            >
              标记垃圾
            </a-button>
            <a-popconfirm
              title="确定要删除这条评论吗？"
              @confirm="() => handleDelete(record)"
              ok-text="确定"
              cancel-text="取消"
            >
              <a-button type="link" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </div>
      </template>
    </template>
  </base-list>

  <!-- 评论详情弹窗 -->
  <comment-detail
    v-model:visible="detailVisible"
    :comment="currentComment"
    @deleted="handleSearch"
  />

  <!-- 回复抽屉 -->
  <a-drawer
    :title="`评论回复 (${currentComment?.reply_count || 0})`"
    placement="right"
    :width="600"
    v-model:open="repliesDrawerVisible"
    :closable="true"
  >
    <template v-if="currentComment">
      <!-- 原评论内容 -->
      <div class="parent-comment">
        <a-comment>
          <template #author>
            <a>{{ currentComment.user_name }}</a>
            <a-tag :color="getStatusColor(currentComment)" class="status-tag">
              {{ getStatusText(currentComment) }}
            </a-tag>
          </template>
          <template #avatar>
            <a-avatar>{{ currentComment.user_name?.[0]?.toUpperCase() }}</a-avatar>
          </template>
          <template #content>
            <p>{{ currentComment.content }}</p>
          </template>
          <template #datetime>
            <a-tooltip :title="formatDate(currentComment.created_at)">
              <span>{{ formatDate(currentComment.created_at) }}</span>
            </a-tooltip>
          </template>
        </a-comment>
        <a-divider />
      </div>

      <!-- 回复列表 -->
      <div v-if="currentComment.replies && currentComment.replies.length > 0" class="replies-list">
        <a-comment v-for="reply in currentComment.replies" :key="reply.id">
          <template #actions>
            <a-space>
              <a v-if="!reply.is_approved && !reply.is_spam" @click="() => handleApprove(reply)">通过</a>
              <a v-if="!reply.is_spam" class="danger-link" @click="() => handleMarkSpam(reply)">标记垃圾</a>
              <a-popconfirm
                title="确定要删除这条回复吗？"
                @confirm="() => handleDelete(reply)"
                ok-text="确定"
                cancel-text="取消"
              >
                <a class="danger-link">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
          <template #author>
            <a>{{ reply.user_name }}</a>
            <a-tag :color="getStatusColor(reply)" class="status-tag">
              {{ getStatusText(reply) }}
            </a-tag>
            <span v-if="reply.parent_id && reply.parent_id !== currentComment.id" class="reply-reference">
              回复 #{{ reply.parent_id }}
            </span>
          </template>
          <template #avatar>
            <a-avatar>{{ reply.user_name?.[0]?.toUpperCase() }}</a-avatar>
          </template>
          <template #content>
            <p>{{ reply.content }}</p>
            <div v-if="reply.reply_count > 0" class="sub-reply-info">
              <a @click="loadSubReplies(reply)">
                <message-outlined />
                {{ reply.reply_count }} 条回复
              </a>
            </div>
          </template>
          <template #datetime>
            <a-tooltip :title="formatDate(reply.created_at)">
              <span>{{ formatDate(reply.created_at) }}</span>
            </a-tooltip>
          </template>
        </a-comment>
      </div>
      <div v-else class="no-replies">暂无回复</div>
    </template>
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { ColumnsType, TablePaginationConfig, FilterValue, SorterResult } from 'ant-design-vue/es/table/interface'
import type { CommentResponse, CommentQuery } from '@/types/comment'
import { COMMENT_STATUS_OPTIONS } from '@/types/comment'
import { getComments, approveComment, markCommentAsSpam, deleteComment } from '@/api/comment'
import { message } from 'ant-design-vue/es'
import dayjs from 'dayjs'
import BaseList from '@/components/BaseList.vue'
import CommentDetail from './Detail.vue'
import { MessageOutlined } from '@ant-design/icons-vue'

// 搜索表单数据
const searchForm = reactive<CommentQuery>({
  keyword: '',
  article_title: '',
  status: 'all',
  start_date: undefined,
  end_date: undefined,
  include_replies: true,
  only_root: false,
  page: 1,
  size: 10
})

// 日期范围
const dateRange = ref<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)

// 评论列表数据
const commentList = ref<CommentResponse[]>([])
const loading = ref(false)

// 分页配置
const pagination = reactive<TablePaginationConfig>({
  total: 0,
  current: 1,
  pageSize: 10,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条`,
  position: ['bottomRight']
})

// 评论详情弹窗控制
const detailVisible = ref<boolean>(false)
const currentComment = ref<CommentResponse | null>(null)
const repliesDrawerVisible = ref<boolean>(false)

// 格式化日期
const formatDate = (date: string): string => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 表格列定义
const columns: ColumnsType<CommentResponse> = [
  {
    title: '评论内容',
    dataIndex: 'content',
    key: 'content',
    width: '30%',
    ellipsis: true
  },
  {
    title: '文章标题',
    dataIndex: 'article_title',
    key: 'article_title',
    width: '20%',
    ellipsis: true
  },
  {
    title: '用户名',
    dataIndex: 'user_name',
    key: 'user_name',
    width: '10%'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '10%'
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: '15%'
  },
  {
    title: '操作',
    key: 'action',
    width: '15%',
    fixed: 'right',
    align: 'center'
  }
]

// 获取评论列表
const fetchCommentList = async (): Promise<void> => {
  loading.value = true
  try {
    const response = await getComments(searchForm)
    const { items, total, page, size } = response.data
    commentList.value = items
    pagination.total = total
    pagination.current = page
    pagination.pageSize = size
  } catch (error) {
    message.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

// 表格变化处理函数
const handleTableChange = (
  pagination: TablePaginationConfig,
  _filters: Record<string, FilterValue | null>,
  _sorter: SorterResult<CommentResponse> | SorterResult<CommentResponse>[]
): void => {
  searchForm.page = pagination.current || 1
  searchForm.size = pagination.pageSize || 10
  fetchCommentList()
}

// 搜索和重置函数
const handleSearch = (e?: Event): void => {
  if (e) {
    e.preventDefault()
  }
  searchForm.page = 1
  fetchCommentList()
}

const handleReset = (e?: Event): void => {
  if (e) {
    e.preventDefault()
  }
  searchForm.keyword = ''
  searchForm.article_title = ''
  searchForm.status = 'all'
  searchForm.only_root = false
  dateRange.value = null
  searchForm.start_date = undefined
  searchForm.end_date = undefined
  handleSearch()
}

// 日期范围变化
const onDateRangeChange = (dates: [dayjs.Dayjs, dayjs.Dayjs] | null, dateStrings: [string, string] | null) => {
  if (dates && dateStrings) {
    searchForm.start_date = dateStrings[0]
    searchForm.end_date = dateStrings[1]
  } else {
    searchForm.start_date = undefined
    searchForm.end_date = undefined
  }
}

// 获取状态文本
const getStatusText = (record: CommentResponse): string => {
  if (record.is_spam) return '垃圾'
  if (record.is_approved) return '已通过'
  return '待审核'
}

// 获取状态颜色
const getStatusColor = (record: CommentResponse): string => {
  if (record.is_spam) return 'red'
  if (record.is_approved) return 'green'
  return 'orange'
}

// 查看详情
const handleViewDetail = (record: CommentResponse): void => {
  currentComment.value = record
  detailVisible.value = true
}

// 通过评论
const handleApprove = async (record: CommentResponse): Promise<void> => {
  try {
    await approveComment(record.id)
    message.success('评论已通过')
    await fetchCommentList()
  } catch (error) {
    message.error('操作失败')
  }
}

// 标记垃圾评论
const handleMarkSpam = async (record: CommentResponse): Promise<void> => {
  try {
    await markCommentAsSpam(record.id)
    message.success('已标记为垃圾评论')
    await fetchCommentList()
  } catch (error) {
    message.error('操作失败')
  }
}

// 删除评论
const handleDelete = async (record: CommentResponse): Promise<void> => {
  try {
    await deleteComment(record.id)
    message.success('评论已删除')
    await fetchCommentList()
  } catch (error) {
    message.error('操作失败')
  }
}

// 显示回复抽屉
const showReplies = (record: CommentResponse) => {
  currentComment.value = record
  repliesDrawerVisible.value = true
}

// 加载子回复
const loadSubReplies = async (reply: CommentResponse) => {
  if (!currentComment.value?.replies) return

  try {
    loading.value = true
    const response = await getComments({
      parent_id: reply.id,
      include_replies: true,
      page: 1,
      size: 100,
      keyword: '',
      article_title: '',
      status: 'all',
      start_date: undefined,
      end_date: undefined,
      only_root: false
    })
    
    const index = currentComment.value.replies.findIndex(r => r.id === reply.id)
    if (index > -1) {
      // 在当前回复后插入其子回复
      currentComment.value.replies.splice(index + 1, 0, ...response.data.items)
    }
  } catch (error) {
    message.error('获取子回复失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取评论列表
onMounted(() => {
  fetchCommentList()
})
</script>

<style scoped>
.comment-content {
  cursor: pointer;
  color: #1890ff;
  margin-bottom: 8px;
}

.comment-content:hover {
  text-decoration: underline;
}

.reply-info {
  margin-top: 4px;
}

.reply-to {
  margin-top: 4px;
  color: rgba(0, 0, 0, 0.45);
}

.operation-column :deep(.ant-btn) {
  padding: 0 4px;
}

.parent-comment {
  margin-bottom: 24px;
}

.replies-list {
  padding-left: 24px;
}

.reply-reference {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-left: 8px;
}

.status-tag {
  margin-left: 8px;
}

.sub-reply-info {
  margin-top: 8px;
}

.danger-link {
  color: #ff4d4f !important;
}

.danger-link:hover {
  color: #ff7875 !important;
}

.no-replies {
  color: rgba(0, 0, 0, 0.45);
  text-align: center;
  padding: 24px;
}

/* 自定义评论组件样式 */
:deep(.ant-comment) {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

:deep(.ant-comment:hover) {
  background: #fafafa;
}

:deep(.ant-comment-nested) {
  margin-left: 24px;
}

:deep(.ant-comment-content-detail) {
  font-size: 14px;
}

:deep(.ant-comment-actions) {
  margin-top: 8px;
}

:deep(.ant-comment-content-author) {
  margin-bottom: 8px;
}

:deep(.ant-comment-content-author-name) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.ant-comment-content-author-time) {
  color: rgba(0, 0, 0, 0.45);
}

.action-column {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
}

.action-column :deep(.ant-space) {
  gap: 8px !important;
}
</style>