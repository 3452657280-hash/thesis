import request from './request'

export const listLaws = (params) => request.get('/public/laws', { params })
export const listLawNames = () => request.get('/public/laws/names')
export const listTemplates = (params) => request.get('/public/templates', { params })
export const templateDownloadUrl = (id) => `/api/public/templates/${id}/download`
export const listNotices = () => request.get('/public/notices')
export const listLawyers = (params) => request.get('/public/lawyers', { params })
