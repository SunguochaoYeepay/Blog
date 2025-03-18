<template>
  <div class="home">
    <Hero />
    <Projects />
    <Contact />
  </div>
</template>

<script setup lang="ts">
import Hero from './components/Hero.vue'
import Projects from './components/Projects.vue'
import Contact from './components/Contact.vue'
</script>

<style scoped>
.home {
  min-height: 100vh;
}
</style>