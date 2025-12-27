import api from './axios'

export const authApi = {
  register: async (data) => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  login: async (data) => {
    const response = await api.post('/auth/login', data)
    return response.data
  },

  refresh: async (refreshToken) => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  getMe: async () => {
    const response = await api.get('/users/me')
    return response.data
  },

  updateMe: async (data) => {
    const response = await api.put('/users/me', data)
    return response.data
  },
}
