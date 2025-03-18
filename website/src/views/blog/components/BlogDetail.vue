<template>
  <div class="blog-detail" v-if="post">
    <div class="blog-hero">
      <img :src="post.coverImage" :alt="post.title" class="cover-image" />
      <div class="hero-content">
        <div class="category-tag">{{ post.category }}</div>
        <h1>{{ post.title }}</h1>
        <div class="post-meta">
          <div class="author-info">
            <img :src="post.author.avatar" :alt="post.author.name" />
            <span>{{ post.author.name }}</span>
          </div>
          <time>{{ formatDate(post.date) }}</time>
        </div>
      </div>
    </div>

    <div class="blog-content">
      <div class="content-wrapper">
        <div class="table-of-contents" v-if="tableOfContents.length > 0">
          <h3>目录</h3>
          <ul>
            <li 
              v-for="(item, index) in tableOfContents" 
              :key="index"
              :class="{ 'toc-h2': item.level === 2, 'toc-h3': item.level === 3 }"
            >
              <a :href="'#' + item.id">{{ item.text }}</a>
            </li>
          </ul>
        </div>

        <article class="markdown-content" v-html="renderedContent"></article>

        <div class="share-buttons">
          <button @click="shareOnTwitter" class="share-btn twitter">
            分享到 Twitter
          </button>
          <button @click="shareOnLinkedIn" class="share-btn linkedin">
            分享到 LinkedIn
          </button>
          <button @click="copyLink" class="share-btn copy">
            复制链接
          </button>
        </div>

        <div class="post-navigation">
          <router-link 
            v-if="previousPost" 
            :to="'/blog/' + previousPost.id" 
            class="prev-post"
          >
            <span>← 上一篇</span>
            <p>{{ previousPost.title }}</p>
          </router-link>
          <router-link 
            v-if="nextPost" 
            :to="'/blog/' + nextPost.id" 
            class="next-post"
          >
            <span>下一篇 →</span>
            <p>{{ nextPost.title }}</p>
          </router-link>
        </div>
      </div>

      <aside class="blog-sidebar">
        <div class="author-card">
          <img :src="post.author.avatar" :alt="post.author.name" />
          <h3>{{ post.author.name }}</h3>
          <p>{{ post.author.bio }}</p>
          <div class="social-links">
            <a href="#" target="_blank" rel="noopener">Twitter</a>
            <a href="#" target="_blank" rel="noopener">GitHub</a>
            <a href="#" target="_blank" rel="noopener">LinkedIn</a>
          </div>
        </div>

        <div class="related-posts">
          <h3>相关文章</h3>
          <div 
            v-for="relatedPost in relatedPosts" 
            :key="relatedPost.id" 
            class="related-post-card"
            @click="navigateToPost(relatedPost.id)"
          >
            <img :src="relatedPost.coverImage" :alt="relatedPost.title" />
            <div>
              <h4>{{ relatedPost.title }}</h4>
              <time>{{ formatDate(relatedPost.date) }}</time>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
  <div v-else class="loading">
    加载中...
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import dayjs from 'dayjs'

// 类型定义
interface Author {
  id: number
  name: string
  avatar: string
  bio: string
}

interface BlogPost {
  id: number
  title: string
  content: string
  coverImage: string
  category: string
  date: string
  author: Author
}

interface TableOfContentsItem {
  id: string
  text: string
  level: number
}

const route = useRoute()
const router = useRouter()

// 状态定义
const post = ref<BlogPost | null>(null)
const tableOfContents = ref<TableOfContentsItem[]>([])
const relatedPosts = ref([
  {
    id: 2,
    title: 'TypeScript 最佳实践指南',
    coverImage: 'https://picsum.photos/300/200?random=2',
    date: '2024-03-18'
  },
  {
    id: 3,
    title: 'Vue Router 4 使用教程',
    coverImage: 'https://picsum.photos/300/200?random=3',
    date: '2024-03-15'
  }
])

const previousPost = ref({
  id: 2,
  title: 'TypeScript 最佳实践指南'
})

const nextPost = ref({
  id: 3,
  title: 'Vue Router 4 使用教程'
})

// 获取文章内容
const fetchPost = async (id: string) => {
  try {
    // 这里应该是实际的 API 调用
    // 现在使用模拟数据
    const mockPost: BlogPost = {
      id: parseInt(id),
      title: 'Vue 3 组合式 API 入门指南',
      content: `# Vue 3 组合式 API 入门指南

## 简介

组合式 API 是 Vue 3 中组织组件逻辑的新方式。它提供了一种更灵活的方式来在组件之间重用代码并组织复杂的组件逻辑。

## 为什么选择组合式 API？

组合式 API 解决了选项式 API 的几个限制：

- 更好的 TypeScript 支持
- 更灵活的代码组织
- 更好的代码复用
- 更可预测的大型组件代码组织

## 基本用法

这是一个使用组合式 API 的简单示例：

<pre class="language-vue"><code>&lt;script setup&gt;
import { ref, onMounted } from 'vue'

const count = ref(0)

const increment = () => {
  count.value++
}

onMounted(() => {
  console.log('组件已挂载！')
})
&lt;/script&gt;</code></pre>

## 高级模式

### 组合式函数

组合式函数是在组件之间重用有状态逻辑的主要方式。它们可以：

- 封装复杂的业务逻辑
- 提供更好的代码组织
- 实现更高的代码复用率

### 生命周期钩子

在组合式 API 中，生命周期钩子可以：

- 在同一个组件中多次使用
- 在组合式函数中使用
- 更灵活地组织相关代码

## 最佳实践

1. 保持组合式函数的专注性
2. 使用有意义的命名
3. 编写清晰的文档
4. 编写测试用例

## 结论

组合式 API 为 Vue 3 提供了一种强大的方式来组织和重用组件逻辑。通过合理使用，可以让代码更容易维护和扩展。`,
      coverImage: 'https://picsum.photos/1200/600?random=1',
      category: 'Vue.js',
      date: '2024-03-20',
      author: {
        id: 1,
        name: '张三',
        avatar: 'https://i.pravatar.cc/100?img=1',
        bio: '全栈开发者，热衷于 Vue.js 和 TypeScript。专注于 Web 开发、最佳实践和开发者效率提升。'
      }
    }
    post.value = mockPost
  } catch (error) {
    console.error('获取文章失败:', error)
  }
}

// 生成目录
const generateTableOfContents = (content: string) => {
  const tokens = marked.lexer(content)
  const toc: TableOfContentsItem[] = []

  tokens.forEach(token => {
    if (token.type === 'heading') {
      const id = token.text.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      toc.push({
        id,
        text: token.text,
        level: token.depth
      })
    }
  })

  return toc
}

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!post.value) return ''
  
  // 渲染 Markdown 并使用类型断言
  const html = marked(post.value.content) as string
  
  // 净化 HTML 字符串
  const sanitizedHtml = DOMPurify.sanitize(html)
  return sanitizedHtml
})

// 分享功能
const shareOnTwitter = () => {
  const url = window.location.href
  const text = post.value?.title
  window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text || '')}`)
}

const shareOnLinkedIn = () => {
  const url = window.location.href
  window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`)
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    // TODO: 使用更友好的提示方式，如 Toast
    alert('链接已复制到剪贴板！')
  } catch (err) {
    console.error('复制链接失败:', err)
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY年M月D日')
}

// 导航到其他文章
const navigateToPost = (postId: number) => {
  router.push(`/blog/${postId}`)
}

// 生命周期钩子
onMounted(async () => {
  const postId = route.params.id as string
  await fetchPost(postId)
  if (post.value) {
    tableOfContents.value = generateTableOfContents(post.value.content)
  }
})
</script>

<style scoped lang="scss">
:root {
  --primary-color: #3b82f6;
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
  --background-primary: #ffffff;
  --background-secondary: #f3f4f6;
}

.blog-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--background-secondary);
}

.blog-hero {
  position: relative;
  height: 400px;
  margin-bottom: 2rem;
  border-radius: 1rem;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
}

.hero-content h1 {
  font-size: 2.5rem;
  margin: 1rem 0;
}

.category-tag {
  display: inline-block;
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-info img {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
}

.blog-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.content-wrapper {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.table-of-contents {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
}

.table-of-contents h3 {
  margin-bottom: 1rem;
}

.table-of-contents ul {
  list-style: none;
  padding: 0;
}

.table-of-contents li {
  margin-bottom: 0.5rem;
}

.table-of-contents a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.3s ease;
}

.table-of-contents a:hover {
  color: var(--primary-color);
}

.toc-h2 {
  margin-left: 0;
}

.toc-h3 {
  margin-left: 1.5rem;
}

.markdown-content {
  line-height: 1.8;
  color: var(--text-primary);
  
  h1, h2, h3, h4, h5, h6 {
    margin: 2rem 0 1rem;
    color: var(--text-primary);
  }

  p {
    margin-bottom: 1.5rem;
  }

  code {
    background: #f1f5f9;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
  }

  pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1.5rem 0;

    code {
      background: none;
      padding: 0;
      color: inherit;
    }
  }

  ul, ol {
    margin: 1.5rem 0;
    padding-left: 2rem;
  }

  img {
    max-width: 100%;
    height: auto;
    border-radius: 0.5rem;
    margin: 1.5rem 0;
  }

  blockquote {
    border-left: 4px solid var(--primary-color);
    padding-left: 1rem;
    margin: 1.5rem 0;
    color: var(--text-secondary);
  }
}

.share-buttons {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
}

.share-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.3s ease;
}

.share-btn:hover {
  opacity: 0.9;
}

.twitter {
  background: #1da1f2;
  color: white;
}

.linkedin {
  background: #0077b5;
  color: white;
}

.copy {
  background: #64748b;
  color: white;
}

.post-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.prev-post,
.next-post {
  flex: 1;
  text-decoration: none;
  color: var(--text-primary);
}

.next-post {
  text-align: right;
}

.post-navigation span {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.post-navigation p {
  margin-top: 0.5rem;
  font-weight: 500;
}

.blog-sidebar {
  position: sticky;
  top: 2rem;
  align-self: start;
}

.author-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.author-card img {
  width: 5rem;
  height: 5rem;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.author-card h3 {
  margin-bottom: 0.5rem;
}

.author-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
}

.social-links a:hover {
  color: var(--primary-color);
}

.related-posts {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.related-posts h3 {
  margin-bottom: 1rem;
}

.related-post-card {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.related-post-card:last-child {
  border-bottom: none;
}

.related-post-card:hover {
  opacity: 0.8;
}

.related-post-card img {
  width: 5rem;
  height: 3rem;
  object-fit: cover;
  border-radius: 0.5rem;
}

.related-post-card h4 {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.related-post-card time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  font-size: 1.25rem;
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .blog-content {
    grid-template-columns: 1fr;
  }

  .blog-sidebar {
    position: static;
    margin-top: 2rem;
  }
}

@media (max-width: 768px) {
  .blog-detail {
    padding: 1rem;
  }

  .blog-hero {
    height: 300px;
  }

  .hero-content h1 {
    font-size: 1.75rem;
  }

  .share-buttons {
    flex-direction: column;
  }

  .post-navigation {
    flex-direction: column;
    gap: 1rem;
  }

  .next-post {
    text-align: left;
  }
}

@media (max-width: 480px) {
  .blog-hero {
    height: 250px;
  }

  .hero-content h1 {
    font-size: 1.5rem;
  }

  .post-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>