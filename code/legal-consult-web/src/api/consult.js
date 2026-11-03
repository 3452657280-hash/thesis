import request from './request'

export const listSessions = () => request.get('/consult/sessions')
export const createSession = () => request.post('/consult/sessions')
export const renameSession = (id, title) => request.put(`/consult/sessions/${id}`, { title })
export const deleteSession = (id) => request.delete(`/consult/sessions/${id}`)
export const listMessages = (id) => request.get(`/consult/sessions/${id}/messages`)

export const addFavorite = (messageId) => request.post(`/consult/messages/${messageId}/favorite`)
export const removeFavorite = (messageId) => request.delete(`/consult/messages/${messageId}/favorite`)
export const listFavorites = () => request.get('/consult/favorites')
export const sendFeedback = (messageId, data) => request.post(`/consult/messages/${messageId}/feedback`, data)
