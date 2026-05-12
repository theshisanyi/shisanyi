<template>
  <div class="similar-sidebar">
    <h3 class="sidebar-title">相似游戏推荐</h3>
    <router-link
      v-for="game in games"
      :key="game.id"
      :to="`/game/${game.id}`"
      class="similar-item"
    >
      <img v-if="game.cover_image" :src="game.cover_image" :alt="game.title" />
      <div v-else class="similar-placeholder">{{ game.title.charAt(0) }}</div>
      <div class="similar-info">
        <h4>{{ game.title }}</h4>
        <span class="similar-rating">★ {{ (game.rating || 0).toFixed(1) }}</span>
      </div>
    </router-link>
    <p v-if="!games.length" class="empty">暂无相似推荐</p>
  </div>
</template>

<script setup>
defineProps({
  games: { type: Array, default: () => [] }
})
</script>

<style scoped>
.similar-sidebar {
  background: #161b22;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #30363d;
}
.sidebar-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #e6edf3;
}
.similar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid #21262d;
  transition: background 0.15s;
}
.similar-item:last-child { border-bottom: none; }
.similar-item:hover { background: #21262d; margin: 0 -8px; padding: 10px 8px; border-radius: 8px; }
.similar-item img, .similar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}
.similar-placeholder {
  background: #21262d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #484f58;
}
.similar-info h4 {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}
.similar-rating {
  font-size: 0.8rem;
  color: #f0883e;
}
.empty {
  color: #484f58;
  font-size: 0.85rem;
}
</style>
