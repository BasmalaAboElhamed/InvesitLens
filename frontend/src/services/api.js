import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const companyService = {
  getCompanies: () => api.get('/companies').then(res => res.data),
  getCompany: (id) => api.get(`/companies/${id}`).then(res => res.data),
  createCompany: (data) => api.post('/companies', data).then(res => res.data),
};

export const documentService = {
  getCompanyDocuments: (companyId) => api.get(`/documents/company/${companyId}`).then(res => res.data),
  uploadDocument: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(res => res.data),
};

export const analysisService = {
  getCompanyAnalyses: (companyId) => api.get(`/analysis/company/${companyId}`).then(res => res.data),
  getAnalysis: (id) => api.get(`/analysis/${id}`).then(res => res.data),
  startAnalysis: (companyId, years) => {
    const params = new URLSearchParams({ company_id: companyId });
    if (years && years.length > 0) {
      years.forEach(y => params.append('years', y));
    }
    return api.post(`/analysis/start?${params.toString()}`).then(res => res.data);
  }
};

export const chatService = {
  askQuestion: (data) => api.post('/chat', data).then(res => res.data),
};

export const reportService = {
  getReport: (analysisId) => api.get(`/reports/${analysisId}`).then(res => res.data),
};

export const systemService = {
  resetAllData: () => api.delete('/reset').then(res => res.data),
};
