import { defineStore } from 'pinia'
import { fetchGames, fetchHotGames, fetchGameDetail } from '../api/games'

export const useGameStore = defineStore('games', {
  state: () => ({
    games: [],
    hotGames: [],
    currentGame: null,
    loading: false,
    ordering: '-sort_weight',
  }),
  actions: {
    async loadGames() {
      this.loading = true
      try {
        this.games = await fetchGames({ ordering: this.ordering })
      } finally {
        this.loading = false
      }
    },
    async loadHotGames() {
      try {
        this.hotGames = await fetchHotGames()
      } catch (e) {
        this.hotGames = []
      }
    },
    async loadGameDetail(id) {
      this.currentGame = await fetchGameDetail(id)
    },
    setOrdering(ordering) {
      this.ordering = ordering
      this.loadGames()
    }
  }
})
