<template>
  <div class="blog-list">
    <div class="blog-header">
      <h1>Blog</h1>
      <div class="blog-filters">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search posts..." 
          class="search-input"
        />
        <select v-model="selectedCategory" class="category-select">
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
    </div>

    <div class="blog-grid">
      <article 
        v-for="post in filteredPosts" 
        :key="post.id" 
        class="blog-card"
        @click="navigateToPost(post.id)"
      >
        <div class="blog-card-image">
          <img :src="post.coverImage" :alt="post.title" />
          <div class="category-tag">{{ post.category }}</div>
        </div>
        <div class="blog-card-content">
          <h2>{{ post.title }}</h2>
          <p class="blog-excerpt">{{ post.excerpt }}</p>
          <div class="blog-meta">
            <div class="blog-author">
              <img :src="post.author.avatar" :alt="post.author.name" />
              <span>{{ post.author.name }}</span>
            </div>
            <time>{{ formatDate(post.date) }}</time>
          </div>
        </div>
      </article>
    </div>

    <div v-if="filteredPosts.length === 0" class="no-results">
      <p>No posts found matching your criteria.</p>
    </div>

    <div class="pagination">
      <button 
        :disabled="currentPage === 1" 
        @click="currentPage--"
        class="pagination-btn"
      >
        Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button 
        :disabled="currentPage === totalPages" 
        @click="currentPage++"
        class="pagination-btn"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

interface Author {
  id: number
  name: string
  avatar: string
}

interface BlogPost {
  id: number
  title: string
  excerpt: string
  content: string
  coverImage: string
  category: string
  date: string
  author: Author
}

// 模拟数据
const posts = ref<BlogPost[]>([
  {
    id: 1,
    title: 'Getting Started with Vue 3 Composition API',
    excerpt: 'Learn how to use Vue 3 Composition API to build scalable applications',
    content: '...',
    coverImage: 'https://picsum.photos/600/400?random=1',
    category: 'Vue.js',
    date: '2024-03-20',
    author: {
      id: 1,
      name: 'John Doe',
      avatar: 'https://i.pravatar.cc/40?img=1'
    }
  },
  {
    id: 2,
    title: 'TypeScript Best Practices',
    excerpt: 'Essential TypeScript patterns and practices for better code',
    content: '...',
    coverImage: 'https://picsum.photos/600/400?random=2',
    category: 'TypeScript',
    date: '2024-03-18',
    author: {
      id: 2,
      name: 'Jane Smith',
      avatar: 'https://i.pravatar.cc/40?img=2'
    }
  },
  // 添加更多模拟数据...
])

const router = useRouter()
const searchQuery = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const postsPerPage = 6

// 获取所有分类
const categories = computed(() => {
  return [...new Set(posts.value.map(post => post.category))]
})

// 过滤和分页逻辑
const filteredPosts = computed(() => {
  let filtered = posts.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(post => 
      post.title.toLowerCase().includes(query) ||
      post.excerpt.toLowerCase().includes(query)
    )
  }

  // 分类过滤
  if (selectedCategory.value) {
    filtered = filtered.filter(post => 
      post.category === selectedCategory.value
    )
  }

  // 分页
  const start = (currentPage.value - 1) * postsPerPage
  const end = start + postsPerPage
  return filtered.slice(start, end)
})

// 计算总页数
const totalPages = computed(() => {
  const filteredTotal = posts.value.filter(post => {
    if (selectedCategory.value && post.category !== selectedCategory.value) {
      return false
    }
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      return post.title.toLowerCase().includes(query) ||
             post.excerpt.toLowerCase().includes(query)
    }
    return true
  }).length
  return Math.ceil(filteredTotal / postsPerPage)
})

// 格式化日期
const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }
  return new Date(dateString).toLocaleDateString(undefined, options)
}

// 导航到博客详情页
const navigateToPost = (postId: number) => {
  router.push(`/blog/${postId}`)
}
</script>

<style scoped>
.blog-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.blog-header {
  margin-bottom: 2rem;
}

.blog-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.blog-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input,
.category-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input {
  flex: 1;
}

.search-input:focus,
.category-select:focus {
  border-color: var(--primary-color);
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.blog-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.blog-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.blog-card-image {
  position: relative;
  height: 200px;
}

.blog-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.category-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
}

.blog-card-content {
  padding: 1.5rem;
}

.blog-card-content h2 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.blog-excerpt {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.blog-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.blog-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.blog-author img {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .blog-filters {
    flex-direction: column;
  }

  .blog-grid {
    grid-template-columns: 1fr;
  }
}
</style>