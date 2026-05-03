import request from '@/utils/request'

export function getPipelineStatus() {
  return request.get('/agent/pipeline/status')
}

export function triggerFullPipeline(data) {
  return request.post('/agent/pipeline/run', data)
}

export function triggerAgent(agentName, data) {
  return request.post(`/agent/${agentName}/run`, data)
}

export function getAgentStatus(agentName) {
  return request.get(`/agent/${agentName}/status`)
}

export function getAgentLogs(params) {
  return request.get('/agent/logs', { params })
}

export function getAllAgentsStatus() {
  return request.get('/agent/status')
}
