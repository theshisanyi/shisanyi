<template>
  <div class="game-detail">
    <h1>游戏详情</h1>
    <p>Game ID: {{ id }}</p>
  </div>
</template>

<script setup>
defineProps({
  id: [String, Number]
})
</script>
