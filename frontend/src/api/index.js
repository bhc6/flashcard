import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.error || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export default {
  healthCheck() {
    return api.get('/health')
  },

  uploadFile(file, onProgress) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: e => onProgress && onProgress(Math.round((e.loaded * 100) / e.total))
    })
  },

  generateFlashcards(sessionId, text = '') {
    return api.post('/generate', { session_id: sessionId, text })
  },

  getFlashcards(sessionId) {
    return api.get('/flashcards', { params: { session_id: sessionId } })
  },

  saveFlashcards(sessionId, flashcards) {
    return api.post('/flashcards', { session_id: sessionId, flashcards })
  },

  updateFlashcard(sessionId, index, question, answer) {
    return api.put(`/flashcards/${index}`, { session_id: sessionId, question, answer })
  },

  deleteFlashcard(sessionId, index) {
    return api.delete(`/flashcards/${index}`, { params: { session_id: sessionId } })
  },

  addFlashcard(sessionId, question, answer) {
    return api.post('/flashcards/add', { session_id: sessionId, question, answer })
  },

  enhanceFlashcards(sessionId, indices = []) {
    return api.post('/enhance', { session_id: sessionId, indices })
  },

  exportFlashcards(sessionId, format) {
    return api.post('/export', { session_id: sessionId, format }, { responseType: 'blob' })
  },

  importJson(flashcards) {
    return api.post('/import-json', { flashcards })
  },

  parseText(text, separator = ';') {
    return api.post('/parse-text', { text, separator })
  }
}
