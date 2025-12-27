import api from './axios'

export const productsApi = {
  getAll: async (params = {}) => {
    const response = await api.get('/products', { params })
    return response.data
  },

  getById: async (id) => {
    const response = await api.get(`/products/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await api.post('/products', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await api.put(`/products/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    await api.delete(`/products/${id}`)
  },
}
