import request from './request'

export const getLawyerProfile = () => request.get('/lawyer/profile')
export const saveLawyerProfile = (data) => request.post('/lawyer/profile', data)
export const listLawyerAppointments = (params) => request.get('/lawyer/appointments', { params })
export const handleAppointment = (id, data) => request.put(`/lawyer/appointments/${id}`, data)
