import request from '@/utils/request'

export function getFeedbackList(params) {
  return request.get('/feedbacks', { params })
}

export function getFeedbackDetail(id) {
  return request.get(`/feedbacks/${id}`)
}

export function createFeedback(data) {
  return request.post('/feedbacks', data)
}

export function updateFeedback(id, data) {
  return request.put(`/feedbacks/${id}`, data)
}

export function deleteFeedback(id) {
  return request.delete(`/feedbacks/${id}`)
}

export function batchCollectFeedback(data) {
  return request.post('/agent/data-collector/run', data)
}

export function analyzeFeedback(id) {
  return request.post(`/feedbacks/${id}/analyze`)
}

export function generateReply(id) {
  return request.post(`/feedbacks/${id}/reply`)
}
