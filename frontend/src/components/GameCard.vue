<template>
  <router-link :to="`/game/${game.id}`" class="game-card">
    <div class="game-card-image">
      <img v-if="game.cover_image" :src="game.cover_image" :alt="game.title" />
      <div v-else class="game-card-placeholder">{{ game.title.charAt(0) }}</div>
    </div>
    <div class="game-card-info">
      <h3 class="game-card-title">{{ game.title }}</h3>
      <div class="game-card-meta">
        <span class="game-card-rating">★ {{ game.rating.toFixed(1) }}</span>
        <span v-if="game.release_date" class="game-card-date">{{ new Date(game.release_date).getFullYear() }}</span>
      </div>
      <div class="game-card-tags">
        <span v-for="cat in game.categories?.slice(0, 3)" :key="cat.id" class="game-card-tag">{{ cat.name }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  game: { type: Object, required: true }
})
</script>

<style scoped>
.game-card {
  display: flex;
  flex-direction: column;
  background: #161b22;
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #30363d;
}
.game-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.game-card-image {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #0d1117;
}
.game-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.game-card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: bold;
  color: #30363d;
  background: #0d1117;
}
.game-card-info {
  padding: 12px 16px 16px;
}
.game-card-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.game-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 0.85rem;
  color: #8b949e;
}
.game-card-rating {
  color: #f0883e;
  font-weight: 600;
}
.game-card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.game-card-tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  background: #21262d;
  border-radius: 10px;
  color: #8b949e;
}
</style>
