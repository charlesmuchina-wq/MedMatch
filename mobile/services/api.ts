/**
 * MedMatch Mobile - API Client
 * Connects to the same backend as the web app
 */
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Use environment variable or default to production
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://karau-meet.preview.emergentagent.com';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      await SecureStore.deleteItemAsync('auth_token');
      // Navigation will be handled by auth context
    }
    return Promise.reject(error);
  }
);

// ============== Auth APIs ==============

export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  
  register: (data: { email: string; password: string; name: string; user_type: string }) =>
    apiClient.post('/auth/register', data),
  
  logout: () => apiClient.post('/auth/logout'),
  
  refreshToken: () => apiClient.post('/auth/refresh-token'),
  
  getProfile: () => apiClient.get('/auth/me'),
};

// ============== Jobs APIs ==============

export const jobsAPI = {
  search: (params: { query?: string; location?: string; page?: number }) =>
    apiClient.get('/jobs/search', { params }),
  
  getJob: (jobId: string) => apiClient.get(`/jobs/${jobId}`),
  
  getRecommendations: () => apiClient.get('/jobs/recommendations'),
  
  saveJob: (jobId: string) => apiClient.post(`/jobs/${jobId}/save`),
  
  unsaveJob: (jobId: string) => apiClient.delete(`/jobs/${jobId}/save`),
  
  getSavedJobs: () => apiClient.get('/jobs/saved'),
  
  applyToJob: (jobId: string, data: any) =>
    apiClient.post(`/jobs/${jobId}/apply`, data),
};

// ============== Resume APIs ==============

export const resumeAPI = {
  upload: (formData: FormData) =>
    apiClient.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  get: () => apiClient.get('/resume'),
  
  update: (data: any) => apiClient.put('/resume', data),
  
  getSkills: () => apiClient.get('/resume/skills'),
  
  parse: (formData: FormData) =>
    apiClient.post('/resume/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// ============== AI Features APIs ==============

export const aiAPI = {
  // Interview Prep
  generateQuestions: (jobTitle: string, numQuestions?: number) =>
    apiClient.post('/interview-prep', { job_title: jobTitle, num_questions: numQuestions }),
  
  generateAnswer: (question: string, context?: string) =>
    apiClient.post('/interview-prep/answer', { question, context }),
  
  // Voice Coach
  getVoiceTips: (topic: string) =>
    apiClient.post('/voice-coach', { mode: 'tips', topic }),
  
  analyzeVoice: (formData: FormData) =>
    apiClient.post('/voice-coach/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  // KARAU Dragon AI Assistant
  sendMessage: (message: string, context?: string) =>
    apiClient.post('/assistant', { message, context }),
  
  // Q&A Practice
  practiceQA: (question: string, answer: string, jobContext?: string) =>
    apiClient.post('/qa-practice', { question, answer, job_context: jobContext }),
  
  // Cover Letter
  generateCoverLetter: (jobId: string) =>
    apiClient.post('/cover-letter/generate', { job_id: jobId }),
};

// ============== Video Interview APIs ==============

export const videoAPI = {
  createSession: (data: { title: string; job_title?: string; questions?: string[] }) =>
    apiClient.post('/video-interview/sessions/create', data),
  
  listSessions: () => apiClient.get('/video-interview/sessions'),
  
  getSession: (sessionId: string) =>
    apiClient.get(`/video-interview/sessions/${sessionId}`),
  
  uploadRecording: (sessionId: string, formData: FormData) =>
    apiClient.post(`/video-interview/sessions/${sessionId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  analyzeVideo: (data: { session_id: string; transcript: string; question?: string }) =>
    apiClient.post('/video-interview/analyze', data),
  
  // Video Analysis with Facial Expression
  getAnalysisStatus: () => apiClient.get('/video-analysis/status'),
  
  analyzeFrame: (data: { image_base64: string; timestamp: number; context?: string }) =>
    apiClient.post('/video-analysis/analyze-frame', data),
  
  getComprehensiveFeedback: (data: { session_id: string; frames_data: any[]; transcript?: string }) =>
    apiClient.post('/video-analysis/comprehensive-feedback', data),
};

// ============== ID Verification APIs ==============

export const verificationAPI = {
  getStatus: () => apiClient.get('/id-verify/status'),
  
  createSession: () => apiClient.post('/id-verify/sessions/create'),
  
  uploadDocument: (sessionId: string, formData: FormData) =>
    apiClient.post(`/id-verify/sessions/${sessionId}/upload-document`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  uploadSelfie: (sessionId: string, data: { selfie_image: string; liveness_score: number }) =>
    apiClient.post(`/id-verify/sessions/${sessionId}/upload-selfie`, { ...data, session_id: sessionId }),
  
  getSessionStatus: (sessionId: string) =>
    apiClient.get(`/id-verify/sessions/${sessionId}`),
  
  getUserVerificationStatus: () => apiClient.get('/id-verify/user-status'),
};

// ============== Real-time STT APIs ==============

export const sttAPI = {
  getStatus: () => apiClient.get('/realtime-stt/status'),
  
  transcribe: (formData: FormData, language?: string) =>
    apiClient.post(`/realtime-stt/transcribe?language=${language || 'en'}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  transcribeBase64: (audio: string, format?: string, language?: string) =>
    apiClient.post('/realtime-stt/transcribe-base64', { audio, format, language }),
  
  getHistory: (limit?: number) =>
    apiClient.get('/realtime-stt/history', { params: { limit } }),
};

// ============== Push Notifications APIs ==============

export const pushAPI = {
  getVapidKey: () => apiClient.get('/webpush/vapid-public-key'),
  
  subscribe: (subscription: { endpoint: string; keys: { p256dh: string; auth: string } }) =>
    apiClient.post('/webpush/subscribe', subscription),
  
  unsubscribe: (endpoint: string) =>
    apiClient.delete('/webpush/unsubscribe', { data: { endpoint } }),
  
  sendTest: () => apiClient.post('/webpush/send-test'),
  
  getStatus: () => apiClient.get('/webpush/status'),
};

// ============== Applications APIs ==============

export const applicationsAPI = {
  list: () => apiClient.get('/applications'),
  
  get: (applicationId: string) => apiClient.get(`/applications/${applicationId}`),
  
  getStats: () => apiClient.get('/applications/stats'),
};

// ============== Messages APIs ==============

export const messagesAPI = {
  getConversations: () => apiClient.get('/messages/conversations'),
  
  getMessages: (conversationId: string) =>
    apiClient.get(`/messages/conversations/${conversationId}`),
  
  sendMessage: (conversationId: string, content: string) =>
    apiClient.post(`/messages/conversations/${conversationId}`, { content }),
  
  getUnreadCount: () => apiClient.get('/messages/unread-count'),
};

export default apiClient;
