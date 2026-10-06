<script setup>
const apiBase = import.meta.env.VITE_API_BASE_URL || "由 Vite /api 代理转发";
</script>

<template>
  <main class="portal-shell">
    <header>
      <p class="eyebrow">SIMULATION2 FRONTEND</p>
      <h1>舆情推演前端项目</h1>
    </header>

    <section class="version-grid">
      <a class="version-card" href="./v1.html">
        <span class="version-tag">V1</span>
        <h2>完整控制台</h2>
        <p>事件、公告、策略、会话控制、Agent 状态、指标和评论分布。</p>
      </a>
      <a class="version-card" href="./v2.html">
        <span class="version-tag">V2</span>
        <h2>单屏控制台</h2>
        <p>左侧状态、中间输入、右侧时机，主界面直接展示 Agent 网络与图表。</p>
      </a>
    </section>

    <footer>
      <span>后端代理：{{ apiBase }}</span>
      <span>开发端口：5173</span>
    </footer>
  </main>
</template>
