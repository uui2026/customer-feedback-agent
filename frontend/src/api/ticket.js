import request from '@/utils/request'

export function getTicketList(params) {
  return request.get('/tickets', { params })
}

export function getTicketDetail(id) {
  return request.get(`/tickets/${id}`)
}

export function createTicket(data) {
  return request.post('/tickets', data)
}

export function updateTicket(id, data) {
  return request.put(`/tickets/${id}`, data)
}

export function updateTicketStatus(id, status) {
  return request.put(`/tickets/${id}/status`, { status })
}

export function assignTicket(id, assignee) {
  return request.patch(`/tickets/${id}/assign`, { assignee })
}

export function deleteTicket(id) {
  return request.delete(`/tickets/${id}`)
}
