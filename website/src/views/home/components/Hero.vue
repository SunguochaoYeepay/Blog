<template>
  <section class="hero">
    <div class="hero-content">
      <div class="hero-text">
        <h1 class="title">
          <span class="greeting">Hello, I'm</span>
          <span class="name">Your Name</span>
        </h1>
        <p class="subtitle">Full Stack Developer & Creative Designer</p>
        <p class="description">
          I craft elegant solutions through code and design, turning ideas into engaging digital experiences.
        </p>
        <div class="cta-buttons">
          <button class="primary-btn" @click="scrollToProjects">
            View My Work
            <span class="icon">→</span>
          </button>
          <button class="secondary-btn" @click="scrollToContact">
            Get in Touch
          </button>
        </div>
      </div>
      <div class="hero-visual">
        <div class="code-window">
          <div class="window-header">
            <div class="window-buttons">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div class="window-title">main.ts</div>
          </div>
          <div class="window-content">
            <pre><code>{{ codeSnippet }}</code></pre>
          </div>
        </div>
      </div>
    </div>
    <div class="hero-background">
      <div class="gradient-sphere"></div>
      <div class="floating-shapes">
        <div v-for="i in 5" :key="i" class="shape" :class="'shape-' + i"></div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const codeSnippet = ref(`interface Developer {
  name: string;
  skills: string[];
  passion: string;
}

const me: Developer = {
  name: "Your Name",
  skills: [
    "TypeScript",
    "Vue.js",
    "Node.js",
    "Python",
    "UI/UX Design"
  ],
  passion: "Building beautiful & 
    functional web apps"
};`)

const scrollToProjects = () => {
  document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' })
}

const scrollToContact = () => {
  document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  // Add animation for floating shapes
  const shapes = document.querySelectorAll('.shape')
  shapes.forEach((shape, index) => {
    const delay = index * 0.2
    shape.animate([
      { transform: 'translateY(0)' },
      { transform: 'translateY(-20px)' },
      { transform: 'translateY(0)' }
    ], {
      duration: 3000,
      delay: delay * 1000,
      iterations: Infinity,
      easing: 'ease-in-out'
    })
  })
})
</script>

<style scoped>
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  position: relative;
  z-index: 2;
}

.hero-text {
  padding: 2rem;
}

.title {
  font-size: 3.5rem;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.greeting {
  display: block;
  font-size: 1.5rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.name {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 1.5rem;
  color: #334155;
  margin-bottom: 1.5rem;
}

.description {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
}

.primary-btn, .secondary-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.primary-btn {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.secondary-btn {
  background: transparent;
  border: 2px solid #3b82f6;
  color: #3b82f6;
}

.secondary-btn:hover {
  background: rgba(59, 130, 246, 0.1);
}

.hero-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}

.code-window {
  background: #1e293b;
  border-radius: 0.75rem;
  overflow: hidden;
  width: 100%;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.window-header {
  background: #334155;
  padding: 0.75rem;
  display: flex;
  align-items: center;
}

.window-buttons {
  display: flex;
  gap: 0.5rem;
}

.window-buttons span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.window-buttons span:nth-child(1) { background: #ef4444; }
.window-buttons span:nth-child(2) { background: #fbbf24; }
.window-buttons span:nth-child(3) { background: #22c55e; }

.window-title {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-left: 1rem;
}

.window-content {
  padding: 1.5rem;
}

.window-content pre {
  margin: 0;
  color: #e2e8f0;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  pointer-events: none;
}

.gradient-sphere {
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.05));
  border-radius: 50%;
  top: -200px;
  right: -200px;
  filter: blur(40px);
}

.floating-shapes {
  position: absolute;
  inset: 0;
}

.shape {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  opacity: 0.1;
}

.shape-1 {
  background: #3b82f6;
  top: 20%;
  left: 10%;
  transform: rotate(15deg);
}

.shape-2 {
  background: #8b5cf6;
  top: 60%;
  left: 20%;
  width: 30px;
  height: 30px;
}

.shape-3 {
  background: #06b6d4;
  top: 30%;
  right: 20%;
  border-radius: 50%;
}

.shape-4 {
  background: #3b82f6;
  bottom: 20%;
  right: 10%;
  transform: rotate(-15deg);
}

.shape-5 {
  background: #8b5cf6;
  bottom: 30%;
  left: 30%;
  width: 25px;
  height: 25px;
  border-radius: 50%;
}

@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .cta-buttons {
    justify-content: center;
  }

  .hero-visual {
    order: -1;
  }

  .code-window {
    max-width: 500px;
  }
}

@media (max-width: 640px) {
  .title {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1.25rem;
  }

  .cta-buttons {
    flex-direction: column;
  }

  .code-window {
    max-width: 100%;
  }
}
</style>