import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import GameDetail from '../views/GameDetail.vue'

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/game/:id', name: 'GameDetail', component: GameDetail, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
