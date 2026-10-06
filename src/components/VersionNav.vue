<script setup>
import { RouterLink } from "vue-router";
</script>

<template>
  <nav class="version-nav">
    <RouterLink to="/">项目首页</RouterLink>
    <RouterLink to="/v1">V1</RouterLink>
    <RouterLink to="/v2">V2</RouterLink>
  </nav>
</template>

<style scoped>
.version-nav {
  position: fixed;
  right: 12px;
  bottom: 12px;
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border: 1px solid rgba(67, 20, 7, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 24px rgba(51, 36, 29, 0.16);
  font: 11px/1.3 "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
}

.version-nav a {
  padding: 5px 8px;
  border-radius: 5px;
  color: #806b60;
  text-decoration: none;
}

.version-nav a:hover,
.version-nav a.router-link-active {
  background: #fde9dc;
  color: #d95f2b;
}
</style>
