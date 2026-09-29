import apiClient, { API_BASE_URL } from './client';

export const analysesApi = {
  // Start analysis from natural language prompt
  createAnalysis: async (prompt, categoryOverride = null) => {
    const response = await apiClient.post('/analyses', {
      prompt,
      category_override: categoryOverride || undefined,
    });
    return response.data;
  },

  // Start analysis from CSV/Excel dataset upload
  uploadDataset: async (file, prompt = '') => {
    const formData = new FormData();
    formData.append('file', file);
    if (prompt) {
      formData.append('prompt', prompt);
    }
    const response = await apiClient.post('/analyses/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Poll analysis execution progress
  getAnalysisStatus: async (analysisId) => {
    const response = await apiClient.get(`/analyses/${analysisId}/status`);
    return response.data;
  },

  // Fetch full report data
  getAnalysisReport: async (analysisId) => {
    const response = await apiClient.get(`/analyses/${analysisId}/report`);
    return response.data;
  },

  // List recent analyses
  listRecentAnalyses: async (limit = 10) => {
    const response = await apiClient.get(`/analyses?limit=${limit}`);
    return response.data;
  },

  // Fetch sources health status
  getSourcesHealth: async () => {
    const response = await apiClient.get('/sources/health');
    return response.data;
  },

  // Get PDF download URL
  getPdfDownloadUrl: (analysisId) => {
    return `${API_BASE_URL}/analyses/${analysisId}/export/pdf`;
  },
};
