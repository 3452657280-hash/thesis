import request from './request'

export const listUsers = (params) => request.get('/admin/users', { params })
export const updateUserStatus = (id, status) => request.put(`/admin/users/${id}/status`, { status })
export const resetUserPassword = (id) => request.put(`/admin/users/${id}/reset-password`)

export const listLawyerAudits = (params) => request.get('/admin/lawyers', { params })
export const auditLawyer = (id, data) => request.put(`/admin/lawyers/${id}/audit`, data)

function crud(base) {
  return {
    list: (params) => request.get(`/admin/${base}`, { params }),
    create: (data) => request.post(`/admin/${base}`, data),
    update: (id, data) => request.put(`/admin/${base}/${id}`, data),
    remove: (id) => request.delete(`/admin/${base}/${id}`)
  }
}

export const lawApi = crud('laws')
export const templateApi = crud('templates')
export const noticeApi = crud('notices')

export const listConsults = (params) => request.get('/admin/consults', { params })
export const getStats = () => request.get('/admin/stats')
