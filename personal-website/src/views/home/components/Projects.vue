<template>
  <section id="projects" class="projects">
    <div class="section-header">
      <h2 class="section-title">Featured Projects</h2>
      <p class="section-subtitle">Some of my recent work</p>
    </div>
    
    <div class="projects-grid">
      <div v-for="project in projects" 
           :key="project.id" 
           class="project-card"
           @mouseenter="project.isHovered = true"
           @mouseleave="project.isHovered = false">
        <div class="project-image">
          <img :src="project.image" :alt="project.title">
          <div class="project-overlay" :class="{ active: project.isHovered }">
            <div class="project-links">
              <a :href="project.demo" target="_blank" class="project-link">
                <span class="icon">🔗</span>
                Live Demo
              </a>
              <a :href="project.github" target="_blank" class="project-link">
                <span class="icon">📂</span>
                Source Code
              </a>
            </div>
          </div>
        </div>
        <div class="project-info">
          <h3 class="project-title">{{ project.title }}</h3>
          <p class="project-description">{{ project.description }}</p>
          <div class="project-tech">
            <span v-for="tech in project.technologies" 
                  :key="tech" 
                  class="tech-tag">
              {{ tech }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Project {
  id: number
  title: string
  description: string
  image: string
  demo: string
  github: string
  technologies: string[]
  isHovered: boolean
}

const projects = ref<Project[]>([
  {
    id: 1,
    title: 'AI-Powered Task Manager',
    description: 'A smart task management application that uses AI to prioritize and categorize tasks.',
    image: 'https://via.placeholder.com/400x300',
    demo: '#',
    github: '#',
    technologies: ['Vue.js', 'TypeScript', 'OpenAI API', 'Node.js'],
    isHovered: false
  },
  {
    id: 2,
    title: 'E-commerce Dashboard',
    description: 'A comprehensive dashboard for managing online stores with real-time analytics.',
    image: 'https://via.placeholder.com/400x300',
    demo: '#',
    github: '#',
    technologies: ['React', 'Redux', 'Firebase', 'Material-UI'],
    isHovered: false
  },
  {
    id: 3,
    title: 'Social Media Analytics',
    description: 'A platform for tracking and analyzing social media performance across multiple platforms.',
    image: 'https://via.placeholder.com/400x300',
    demo: '#',
    github: '#',
    technologies: ['Angular', 'D3.js', 'Python', 'FastAPI'],
    isHovered: false
  }
])
</script>

<style scoped>
.projects {
  padding: 6rem 2rem;
  background: #f8fafc;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 1rem;
}

.section-subtitle {
  color: #64748b;
  font-size: 1.125rem;
}

.projects-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.project-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.project-image {
  position: relative;
  padding-top: 66.67%; /* 3:2 aspect ratio */
  overflow: hidden;
}

.project-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.project-card:hover .project-image img {
  transform: scale(1.05);
}

.project-overlay {
  position: absolute;
  inset: 0;
  background: rgba(30, 41, 59, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.project-overlay.active {
  opacity: 1;
}

.project-links {
  display: flex;
  gap: 1rem;
}

.project-link {
  background: white;
  color: #1e293b;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s ease;
}

.project-link:hover {
  transform: scale(1.05);
}

.project-info {
  padding: 1.5rem;
}

.project-title {
  font-size: 1.25rem;
  color: #1e293b;
  margin-bottom: 0.75rem;
}

.project-description {
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.project-tech {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-tag {
  background: #f1f5f9;
  color: #3b82f6;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .section-title {
    font-size: 2rem;
  }
}
</style>