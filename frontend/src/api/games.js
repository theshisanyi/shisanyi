import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export function fetchGames(params) {
  return api.get('/games/', { params }).then(r => r.data)
}

export function fetchHotGames() {
  return api.get('/games/', { params: { is_hot: 'true' } }).then(r => r.data)
}

export function fetchGameDetail(id) {
  return api.get(`/games/${id}/`).then(r => r.data)
}

export function fetchCategories() {
  return api.get('/categories/').then(r => r.data)
}
