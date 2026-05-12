<template>
  <div id="app">
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="header-logo">游戏推荐</router-link>
        <nav class="header-nav">
          <router-link to="/">首页</router-link>
          <a href="http://localhost:8000/admin/" target="_blank">管理后台</a>
        </nav>
      </div>
    </header>
    <router-view />
  </div>
</template>

<script setup>
</script>

<style>
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #21262d;
  --border: #30363d;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #484f58;
  --accent: #1f6feb;
  --rating: #f0883e;
  --success: #238636;
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}
#app {
  min-height: 100vh;
}
.app-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-logo {
  font-size: 1.2rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--text-primary);
}
.header-nav {
  display: flex;
  gap: 20px;
}
.header-nav a {
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  transition: color 0.2s;
}
.header-nav a:hover { color: var(--text-primary); }
.router-link-active:not(.header-logo) { color: var(--accent); }
</style>
