<template>
  <div class="sort-bar">
    <span class="sort-label">排序：</span>
    <button
      v-for="opt in sortOptions"
      :key="opt.value"
      :class="{ active: store.ordering === opt.value }"
      @click="store.setOrdering(opt.value)"
    >{{ opt.label }}</button>
  </div>
</template>

<script setup>
import { useGameStore } from '../stores/games'

const store = useGameStore()
const sortOptions = [
  { label: '按热度', value: '-sort_weight' },
  { label: '按日期', value: '-release_date' },
  { label: '按评分', value: '-rating' },
]
</script>

<style scoped>
.sort-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}
.sort-label {
  color: #8b949e;
  font-size: 0.9rem;
  margin-right: 4px;
}
.sort-bar button {
  padding: 6px 16px;
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #8b949e;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.sort-bar button:hover { color: #e6edf3; }
.sort-bar button.active {
  background: #1f6feb;
  border-color: #1f6feb;
  color: #fff;
}
</style>
