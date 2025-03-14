<template>
  <div class="auth-layout">
    <router-view></router-view>
  </div>
</template>

<script setup lang="ts">
// 空的setup，因为这是一个简单的布局组件
</script>

<style scoped>
.auth-layout {
  width: 100%;
  min-height: 100vh;
}
</style>