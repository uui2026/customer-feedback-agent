import request from '@/utils/request'

export function getDashboardStats() {
  return request.get('/dashboard/stats')
}

export function getChannelDistribution() {
  return request.get('/dashboard/channels')
}

export function getIntentDistribution() {
  return request.get('/dashboard/intents')
}

export function getSentimentDistribution() {
  return request.get('/dashboard/sentiments')
}

export function getTrendData(days = 7) {
  return request.get('/dashboard/trends', { params: { days } })
}

export function getRecentFeedback(limit = 10) {
  return request.get('/dashboard/recent-feedback', { params: { limit } })
}

export function getSlaAlerts() {
  return request.get('/dashboard/sla-alerts')
}
