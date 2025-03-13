<template>
  <div class="app">
    <a-layout>
      <a-layout-header class="header">
        <h1 class="title">用户管理系统</h1>
      </a-layout-header>
      <a-layout-content>
        <user-search />
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import UserSearch from './components/UserSearch.vue';

export default defineComponent({
  name: 'App',
  components: {
    UserSearch,
  },
});
</script>

<style>
.app {
  min-height: 100vh;
}

.header {
  background: #fff;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.title {
  margin: 0;
  color: #1890ff;
  line-height: 64px;
}
</style> 