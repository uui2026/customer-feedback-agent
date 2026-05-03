import request from '@/utils/request'

export function getKnowledgeList(params) {
  return request.get('/knowledge', { params })
}

export function getKnowledgeDetail(id) {
  return request.get(`/knowledge/${id}`)
}

export function createKnowledge(data) {
  return request.post('/knowledge', data)
}

export function updateKnowledge(id, data) {
  return request.put(`/knowledge/${id}`, data)
}

export function deleteKnowledge(id) {
  return request.delete(`/knowledge/${id}`)
}

export function searchKnowledge(keyword) {
  return request.get('/knowledge/search', { params: { q: keyword } })
}

export function getKnowledgeCategories() {
  return request.get('/knowledge/categories')
}
