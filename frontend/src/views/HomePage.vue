<template>
  <div class="home-page">
    <HotCarousel :hot-games="store.hotGames" />
    <SortBar />
    <div v-if="store.loading" class="loading">加载中...</div>
    <div v-else class="game-grid">
      <GameCard v-for="game in store.games" :key="game.id" :game="game" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useGameStore } from '../stores/games'
import HotCarousel from '../components/HotCarousel.vue'
import SortBar from '../components/SortBar.vue'
import GameCard from '../components/GameCard.vue'

const store = useGameStore()

onMounted(() => {
  store.loadHotGames()
  store.loadGames()
})
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
.loading {
  text-align: center;
  color: #8b949e;
  padding: 40px;
  font-size: 1rem;
}
</style>
