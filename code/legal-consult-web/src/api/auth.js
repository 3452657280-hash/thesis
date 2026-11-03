import request from './request'

export const register = (data) => request.post('/auth/register', data)
export const login = (data) => request.post('/auth/login', data)
export const getMe = () => request.get('/user/me')
export const updateMe = (data) => request.put('/user/me', data)
export const updatePassword = (data) => request.put('/user/password', data)
