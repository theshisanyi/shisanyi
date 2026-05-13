<template>
  <div class="game-detail-page" v-if="game">
    <!-- Blurred background -->
    <img v-if="game.cover_image" :src="game.cover_image" class="blur-bg" />
    <div class="blur-overlay"></div>

    <!-- Back button -->
    <div class="detail-content">
      <router-link to="/" class="back-btn">← 返回首页</router-link>
      <!-- Hero -->
      <div class="detail-hero">
        <img v-if="game.cover_image" :src="game.cover_image" :alt="game.title" class="detail-cover" />
        <div class="detail-hero-info">
          <h1 class="detail-title">{{ game.title }}</h1>
          <div class="detail-meta">
            <span class="detail-rating">★ {{ (game.rating || 0).toFixed(1) }}</span>
            <span v-if="game.play_duration" class="detail-duration">{{ game.play_duration }}</span>
            <span v-if="game.release_date" class="detail-date">{{ new Date(game.release_date).toLocaleDateString('zh-CN') }}</span>
          </div>
          <div class="detail-tags">
            <span v-for="cat in game.categories" :key="cat.id" class="detail-tag">{{ cat.name }}</span>
          </div>
          <a v-if="game.purchase_link" :href="game.purchase_link" target="_blank" class="detail-buy-btn">前往购买</a>
        </div>
      </div>

      <!-- Two columns -->
      <div class="detail-body">
        <!-- Main content -->
        <div class="detail-main">
          <section v-if="game.official_intro" class="detail-section">
            <h2>游戏简介</h2>
            <p>{{ game.official_intro }}</p>
          </section>
          <section v-if="game.review" class="detail-section">
            <h2>评测心得</h2>
            <div v-html="game.review" class="review-content"></div>
          </section>
        </div>

        <!-- Sidebar -->
        <aside class="detail-sidebar">
          <SimilarGamesSidebar :games="game.similar_games || []" />
        </aside>
      </div>
    </div>
  </div>
  <div v-else class="loading">加载中...</div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useGameStore } from '../stores/games'
import SimilarGamesSidebar from '../components/SimilarGamesSidebar.vue'

const route = useRoute()
const store = useGameStore()
const game = computed(() => store.currentGame)

onMounted(() => {
  store.loadGameDetail(route.params.id)
})
</script>

<style scoped>
.game-detail-page {
  position: relative;
  min-height: 100vh;
}
.blur-bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  filter: blur(20px);
  opacity: 0.35;
  transform: scale(1.05);
  z-index: -2;
}
.blur-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(13, 17, 23, 0.4);
  z-index: -1;
}
.back-btn {
  display: inline-block;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: 16px;
  transition: color 0.2s;
}
.back-btn:hover { color: var(--text-primary); }

.detail-content {
  position: relative;
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px 60px;
}
.detail-hero {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  background: rgba(22, 27, 34, 0.85);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #30363d;
}
.detail-cover {
  width: 200px;
  height: 280px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}
.detail-hero-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.detail-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 12px;
}
.detail-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 0.95rem;
  color: #8b949e;
}
.detail-rating { color: #f0883e; font-weight: 600; }
.detail-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.detail-tag {
  padding: 4px 12px;
  background: #21262d;
  border-radius: 12px;
  font-size: 0.8rem;
  color: #8b949e;
}
.detail-buy-btn {
  display: inline-block;
  align-self: flex-start;
  padding: 8px 20px;
  background: #238636;
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.detail-buy-btn:hover { background: #2ea043; }
.detail-body {
  display: flex;
  gap: 24px;
}
.detail-main {
  flex: 1;
  min-width: 0;
}
.detail-sidebar {
  width: 280px;
  flex-shrink: 0;
}
.detail-section {
  background: rgba(22, 27, 34, 0.85);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid #30363d;
}
.detail-section h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #30363d;
}
.detail-section p {
  line-height: 1.7;
  color: #c9d1d9;
}
.review-content { line-height: 1.8; color: #c9d1d9; }
.review-content :deep(img) { max-width: 100%; border-radius: 8px; }
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: #8b949e;
}

@media (max-width: 768px) {
  .detail-hero { flex-direction: column; align-items: center; text-align: center; }
  .detail-cover { width: 160px; height: 224px; }
  .detail-title { font-size: 1.5rem; }
  .detail-body { flex-direction: column; }
  .detail-sidebar { width: 100%; }
  .detail-meta { justify-content: center; flex-wrap: wrap; }
  .detail-tags { justify-content: center; }
}
</style>
