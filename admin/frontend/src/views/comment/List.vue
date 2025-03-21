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
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'content'">
        <div>
          <div class="comment-content" :class="{ 'reply-indent': record.parent_id }" @click="handleViewDetail(record)">
            {{ record.content }}
          </div>
          <div v-if="record.reply_count > 0" class="reply-info">
            <a-button type="link" @click="handleViewDetail(record)">
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

  <!-- 评论详情抽屉 -->
  <comment-drawer
    v-model:visible="drawerVisible"
    :comment="currentComment"
    @refresh="handleSearch"
  />
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { ColumnsType, TablePaginationConfig } from 'ant-design-vue/es/table/interface'
import type { CommentResponse, CommentQuery } from '@/types/comment'
import { COMMENT_STATUS_OPTIONS } from '@/types/comment'
import { getComments, getCommentTree, approveComment, markCommentAsSpam, deleteComment } from '@/api/comment'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import BaseList from '@/components/BaseList.vue'
import CommentDrawer from '@/components/comment/CommentDrawer.vue'
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
  page_size: 10
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

// 评论详情抽屉控制
const drawerVisible = ref<boolean>(false)
const currentComment = ref<CommentResponse | null>(null)

// 表格列定义
const columns: ColumnsType<CommentResponse> = [
  {
    title: '评论内容',
    dataIndex: 'content',
    key: 'content',
    width: '40%',
    key: 'content'
  },
  {
    title: '文章',
    dataIndex: 'article_title',
    key: 'article_title',
    width: '20%'
  },
  {
    title: '评论人',
    dataIndex: 'user_name',
    key: 'user_name',
    width: '10%'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '10%',
    key: 'status'
  },
  {
    title: '评论时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: '15%',
    sorter: true,
    defaultSortOrder: 'descend'
  },
  {
    title: '操作',
    key: 'action',
    width: '15%',
    fixed: 'right',
    key: 'action'
  }
]

// 获取评论列表
const handleSearch = async () => {
  loading.value = true
  try {
    const response = await getComments({
      ...searchForm,
      page: pagination.current,
      page_size: pagination.pageSize
    })
    commentList.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    message.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    article_title: '',
    status: 'all',
    start_date: undefined,
    end_date: undefined,
    include_replies: true,
    only_root: false
  })
  dateRange.value = null
  handleSearch()
}

// 表格变化处理
const handleTableChange = (
  pag: TablePaginationConfig,
  filters: Record<string, any>,
  sorter: any
) => {
  pagination.current = pag.current || 1
  pagination.pageSize = pag.pageSize || 10
  if (sorter.field) {
    searchForm.sort_field = sorter.field
    searchForm.sort_order = sorter.order
  }
  handleSearch()
}

// 日期范围变化处理
const onDateRangeChange = (dates: [dayjs.Dayjs, dayjs.Dayjs] | null) => {
  if (dates) {
    searchForm.start_date = dates[0].format('YYYY-MM-DD')
    searchForm.end_date = dates[1].format('YYYY-MM-DD')
  } else {
    searchForm.start_date = undefined
    searchForm.end_date = undefined
  }
}

// 查看评论详情
const handleViewDetail = async (comment: CommentResponse) => {
  try {
    // 先获取完整的评论信息（包括子评论）
    const response = await getCommentTree(comment.article_id)
    // 找到当前评论
    const fullComment = findCommentInTree(response.data, comment.id)
    if (fullComment) {
      currentComment.value = fullComment
      drawerVisible.value = true
    } else {
      message.error('获取评论详情失败')
    }
  } catch (error) {
    message.error('获取评论详情失败')
  }
}

// 在评论树中查找指定评论
const findCommentInTree = (comments: CommentResponse[], targetId: number): CommentResponse | null => {
  for (const comment of comments) {
    if (comment.id === targetId) {
      return comment
    }
    if (comment.replies?.length) {
      const found = findCommentInTree(comment.replies, targetId)
      if (found) {
        return found
      }
    }
  }
  return null
}

// 评论操作处理
const handleApprove = async (comment: CommentResponse) => {
  try {
    await approveComment(comment.id)
    message.success('评论已通过审核')
    handleSearch()
  } catch (error) {
    message.error('操作失败')
  }
}

const handleMarkSpam = async (comment: CommentResponse) => {
  try {
    await markCommentAsSpam(comment.id)
    message.success('已标记为垃圾评论')
    handleSearch()
  } catch (error) {
    message.error('操作失败')
  }
}

const handleDelete = async (comment: CommentResponse) => {
  try {
    await deleteComment(comment.id)
    message.success('评论已删除')
    handleSearch()
  } catch (error) {
    message.error('删除失败')
  }
}

// 获取评论状态文本
const getStatusText = (comment: CommentResponse) => {
  if (comment.is_spam) return '垃圾评论'
  if (comment.is_approved) return '已通过'
  return '待审核'
}

// 获取评论状态颜色
const getStatusColor = (comment: CommentResponse) => {
  if (comment.is_spam) return 'red'
  if (comment.is_approved) return 'green'
  return 'orange'
}

onMounted(() => {
  handleSearch()
})
</script>

<style lang="scss" scoped>
.comment-content {
  cursor: pointer;
  &:hover {
    color: #1890ff;
  }
}

.reply-info {
  margin-top: 4px;
  color: #999;
}

.reply-to {
  margin-top: 4px;
  color: #999;
}

.action-column {
  white-space: nowrap;
  display: flex;
  gap: 8px;
  
  :deep(.ant-btn) {
    padding: 4px 0;
    height: auto;
  }
}
</style>