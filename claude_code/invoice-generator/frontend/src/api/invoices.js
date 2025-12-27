import api from './axios'

export const invoicesApi = {
  getAll: async (params = {}) => {
    const response = await api.get('/invoices', { params })
    return response.data
  },

  getById: async (id) => {
    const response = await api.get(`/invoices/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await api.post('/invoices', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await api.put(`/invoices/${id}`, data)
    return response.data
  },

  updateStatus: async (id, status) => {
    const response = await api.patch(`/invoices/${id}/status`, { status })
    return response.data
  },

  delete: async (id) => {
    await api.delete(`/invoices/${id}`)
  },

  downloadPdf: async (id) => {
    const response = await api.get(`/invoices/${id}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  sendEmail: async (id) => {
    const response = await api.post(`/invoices/${id}/email`)
    return response.data
  },

  getDashboardStats: async () => {
    const response = await api.get('/dashboard/stats')
    return response.data
  },

  getRevenueChart: async (months = 6) => {
    const response = await api.get('/dashboard/revenue', { params: { months } })
    return response.data
  },

  getRecentInvoices: async (limit = 5) => {
    const response = await api.get('/dashboard/recent', { params: { limit } })
    return response.data
  },
}
