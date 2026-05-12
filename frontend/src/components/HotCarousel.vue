<template>
  <div class="carousel" v-if="hotGames.length">
    <div class="carousel-track" :style="{ transform: `translateX(-${current * 100}%)` }">
      <div
        v-for="game in hotGames"
        :key="game.id"
        class="carousel-slide"
      >
        <router-link :to="`/game/${game.id}`" class="carousel-link">
          <img v-if="game.cover_image" :src="game.cover_image" :alt="game.title" />
          <div class="carousel-overlay">
            <h2>{{ game.title }}</h2>
            <p>★ {{ game.rating?.toFixed(1) || 'N/A' }}</p>
          </div>
        </router-link>
      </div>
    </div>
    <button class="carousel-btn carousel-prev" @click="prev" v-if="hotGames.length > 1">‹</button>
    <button class="carousel-btn carousel-next" @click="next" v-if="hotGames.length > 1">›</button>
    <div class="carousel-dots" v-if="hotGames.length > 1">
      <span
        v-for="(_, i) in hotGames"
        :key="i"
        :class="{ active: i === current }"
        @click="goTo(i)"
      ></span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  hotGames: { type: Array, default: () => [] }
})

const current = ref(0)
let timer = null

function next() {
  current.value = (current.value + 1) % props.hotGames.length
}

function prev() {
  current.value = (current.value - 1 + props.hotGames.length) % props.hotGames.length
}

function goTo(i) {
  current.value = i
}

function startAuto() {
  stopAuto()
  timer = setInterval(next, 5000)
}
function stopAuto() {
  if (timer) { clearInterval(timer); timer = null }
}

onMounted(startAuto)
onUnmounted(stopAuto)
</script>

<style scoped>
.carousel {
  position: relative;
  width: 100%;
  aspect-ratio: 21 / 9;
  overflow: hidden;
  border-radius: 12px;
  margin-bottom: 32px;
  background: #161b22;
}
.carousel-track {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}
.carousel-slide {
  min-width: 100%;
  height: 100%;
}
.carousel-link {
  display: block;
  width: 100%;
  height: 100%;
  position: relative;
}
.carousel-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.carousel-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 40px 24px 24px;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: #fff;
}
.carousel-overlay h2 {
  font-size: 1.5rem;
  margin-bottom: 4px;
}
.carousel-overlay p {
  color: #f0883e;
  font-size: 1rem;
}
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0,0,0,0.5);
  color: #fff;
  border: none;
  width: 40px;
  height: 60px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
.carousel-btn:hover { background: rgba(0,0,0,0.8); }
.carousel-prev { left: 0; border-radius: 0 8px 8px 0; }
.carousel-next { right: 0; border-radius: 8px 0 0 8px; }
.carousel-dots {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}
.carousel-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  cursor: pointer;
  transition: background 0.2s;
}
.carousel-dots span.active { background: #f0883e; }
</style>
