import request from './request'

export const createAppointment = (data) => request.post('/appointments', data)
export const myAppointments = () => request.get('/appointments/my')
