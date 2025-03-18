<!-- Logo.vue -->
<template>
  <div class="logo" :class="{ 'animate': isAnimating }">
    <div class="logo-container">
      <div class="brain-circuit">
        <div class="brain">
          <div class="circuit-lines">
            <div class="line line-1"></div>
            <div class="line line-2"></div>
            <div class="line line-3"></div>
          </div>
          <div class="nodes">
            <div class="node node-1"></div>
            <div class="node node-2"></div>
            <div class="node node-3"></div>
          </div>
        </div>
      </div>
      <div class="text">
        <span class="ai">AI</span>
        <span class="dev">Dev</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'

export default defineComponent({
  name: 'Logo',
  setup() {
    const isAnimating = ref(false)

    const startAnimation = () => {
      isAnimating.value = true
      setTimeout(() => {
        isAnimating.value = false
      }, 2000)
    }

    onMounted(() => {
      startAnimation()
      // 每30秒重复一次动画
      setInterval(startAnimation, 30000)
    })

    return {
      isAnimating
    }
  }
})
</script>

<style scoped>
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brain-circuit {
  width: 40px;
  height: 40px;
  position: relative;
}

.brain {
  width: 100%;
  height: 100%;
  border: 2px solid var(--primary-color, #3498db);
  border-radius: 50%;
  position: relative;
  overflow: hidden;
}

.circuit-lines .line {
  position: absolute;
  background: var(--primary-color, #3498db);
  height: 2px;
}

.line-1 {
  width: 60%;
  top: 30%;
  left: 20%;
  transform: rotate(15deg);
}

.line-2 {
  width: 40%;
  top: 50%;
  left: 30%;
  transform: rotate(-20deg);
}

.line-3 {
  width: 50%;
  top: 70%;
  left: 25%;
  transform: rotate(10deg);
}

.nodes .node {
  position: absolute;
  width: 6px;
  height: 6px;
  background: var(--primary-color, #3498db);
  border-radius: 50%;
}

.node-1 {
  top: 20%;
  left: 70%;
}

.node-2 {
  top: 45%;
  left: 20%;
}

.node-3 {
  top: 70%;
  left: 65%;
}

.text {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-color, #2c3e50);
}

.ai {
  color: var(--primary-color, #3498db);
}

.dev {
  margin-left: 0.25rem;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes glow {
  0% {
    box-shadow: 0 0 5px var(--primary-color, #3498db);
  }
  50% {
    box-shadow: 0 0 15px var(--primary-color, #3498db);
  }
  100% {
    box-shadow: 0 0 5px var(--primary-color, #3498db);
  }
}

.animate .brain {
  animation: pulse 2s ease-in-out, glow 2s ease-in-out;
}

.animate .node {
  animation: glow 2s ease-in-out;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .brain-circuit {
    width: 32px;
    height: 32px;
  }

  .text {
    font-size: 1.25rem;
  }
}
</style>