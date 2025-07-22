import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('hiresmart_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('hiresmart_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  phone_number?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  phone_number?: string;
}

interface InterviewSession {
  id: number;
  session_id: string;
  title: string;
  interview_type: string;
  status: string;
  scheduled_at?: string;
  started_at?: string;
  ended_at?: string;
  duration_minutes?: number;
  overall_score?: number;
  confidence_score?: number;
  communication_score?: number;
  technical_score?: number;
  created_at: string;
}

interface Assessment {
  id: number;
  assessment_id: string;
  title: string;
  assessment_type: string;
  category?: string;
  difficulty_level: string;
  time_limit_minutes: number;
  status: string;
  overall_score?: number;
  percentage_score?: number;
  created_at: string;
}

// Authentication API
export const authAPI = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/v1/auth/login', { email, password });
    return response.data;
  },

  register: async (userData: RegisterData): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/v1/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (token?: string): Promise<User> => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    const response = await apiClient.get('/api/v1/auth/me', config);
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/v1/auth/logout');
  },
};

// User API
export const userAPI = {
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get('/api/v1/users/profile');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await apiClient.put('/api/v1/users/profile', userData);
    return response.data;
  },

  uploadResume: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/v1/users/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getResumes: async (): Promise<any[]> => {
    const response = await apiClient.get('/api/v1/users/resumes');
    return response.data;
  },
};

// Interview API
export const interviewAPI = {
  createJobDescription: async (jobData: any): Promise<any> => {
    const response = await apiClient.post('/api/v1/interview/job-description', jobData);
    return response.data;
  },

  getJobDescriptions: async (): Promise<any[]> => {
    const response = await apiClient.get('/api/v1/interview/job-descriptions');
    return response.data;
  },

  createSession: async (sessionData: any): Promise<InterviewSession> => {
    const response = await apiClient.post('/api/v1/interview/session', sessionData);
    return response.data;
  },

  getSessions: async (): Promise<InterviewSession[]> => {
    const response = await apiClient.get('/api/v1/interview/sessions');
    return response.data;
  },

  getSession: async (sessionId: string): Promise<InterviewSession> => {
    const response = await apiClient.get(`/api/v1/interview/session/${sessionId}`);
    return response.data;
  },

  startSession: async (sessionId: string): Promise<void> => {
    await apiClient.post(`/api/v1/interview/session/${sessionId}/start`);
  },

  endSession: async (sessionId: string): Promise<void> => {
    await apiClient.post(`/api/v1/interview/session/${sessionId}/end`);
  },

  getSessionQuestions: async (sessionId: string): Promise<any[]> => {
    const response = await apiClient.get(`/api/v1/interview/session/${sessionId}/questions`);
    return response.data;
  },

  getSessionAnalysis: async (sessionId: string): Promise<any> => {
    const response = await apiClient.get(`/api/v1/interview/session/${sessionId}/analysis`);
    return response.data;
  },
};

// Assessment API
export const assessmentAPI = {
  createAssessment: async (assessmentData: any): Promise<Assessment> => {
    const response = await apiClient.post('/api/v1/assessment/create', assessmentData);
    return response.data;
  },

  getAssessments: async (): Promise<Assessment[]> => {
    const response = await apiClient.get('/api/v1/assessment/list');
    return response.data;
  },

  getAssessment: async (assessmentId: string): Promise<Assessment> => {
    const response = await apiClient.get(`/api/v1/assessment/${assessmentId}`);
    return response.data;
  },

  startAssessment: async (assessmentId: string): Promise<void> => {
    await apiClient.post(`/api/v1/assessment/${assessmentId}/start`);
  },

  getCodingProblems: async (assessmentId: string): Promise<any[]> => {
    const response = await apiClient.get(`/api/v1/assessment/${assessmentId}/coding-problems`);
    return response.data;
  },

  submitCode: async (assessmentId: string, problemId: number, code: string, language: string): Promise<any> => {
    const response = await apiClient.post(
      `/api/v1/assessment/${assessmentId}/coding-problems/${problemId}/submit`,
      { code, programming_language: language }
    );
    return response.data;
  },
};

// AI Analysis API
export const aiAPI = {
  generateQuestions: async (requestData: any): Promise<any[]> => {
    const response = await apiClient.post('/api/v1/ai/generate-questions', requestData);
    return response.data;
  },

  analyzeText: async (text: string, analysisType: string): Promise<any> => {
    const response = await apiClient.post('/api/v1/ai/analyze-text', {
      text_content: text,
      analysis_type: analysisType,
    });
    return response.data;
  },

  getFeedbackSuggestions: async (metrics: any): Promise<any> => {
    const response = await apiClient.get('/api/v1/ai/feedback-suggestions', {
      params: metrics,
    });
    return response.data;
  },

  evaluateAnswer: async (question: string, answer: string, criteria: string[]): Promise<any> => {
    const response = await apiClient.post('/api/v1/ai/evaluate-answer', {
      question,
      answer,
      expected_criteria: criteria,
    });
    return response.data;
  },

  getModelStatus: async (): Promise<any> => {
    const response = await apiClient.get('/api/v1/ai/model-status');
    return response.data;
  },
};

export default apiClient;
