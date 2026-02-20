/**
 * API service for communicating with the backend.
 */
import axios, { AxiosError, CancelTokenSource } from 'axios';
import { AnalysisResponse } from '@/types';

interface ImportMetaEnv {
  VITE_API_URL?: string;
}

const API_BASE_URL = ((import.meta as { env: ImportMetaEnv }).env.VITE_API_URL) || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

let cancelTokenSource: CancelTokenSource | null = null;

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    }
    if (axios.isCancel(error)) {
      throw new Error('Request cancelled');
    }
    return Promise.reject(error);
  }
);

// Error handler
const handleError = (error: AxiosError): never => {
  if (axios.isCancel(error)) {
    throw new Error('Request cancelled');
  }
  if (error.response) {
    const data = error.response.data as { detail?: string; message?: string } | undefined;
    const message = data?.detail || data?.message || 'An error occurred';
    throw new Error(message);
  } else if (error.request) {
    throw new Error('Unable to connect to server. Please check your connection.');
  } else {
    throw new Error('Request failed. Please try again.');
  }
};

// Cancel ongoing requests
export const cancelRequests = () => {
  if (cancelTokenSource) {
    cancelTokenSource.cancel('Operation cancelled by user');
    cancelTokenSource = null;
  }
};

// Create new cancel token
const getCancelToken = () => {
  cancelTokenSource = axios.CancelToken.source();
  return cancelTokenSource.token;
};

export const analyzeImage = async (file: File, isLive: boolean = false): Promise<AnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_live', isLive.toString());
    
    const response = await api.post<AnalysisResponse>('/analyze/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      cancelToken: getCancelToken(),
    });
    
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
};

export const analyzeVideo = async (file: File): Promise<AnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<AnalysisResponse>('/analyze/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      cancelToken: getCancelToken(),
    });
    
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
};

export const analyzeAudio = async (file: File): Promise<AnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<AnalysisResponse>('/analyze/audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      cancelToken: getCancelToken(),
    });
    
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
};

export const analyzeDocument = async (file: File): Promise<AnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<AnalysisResponse>('/analyze/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      cancelToken: getCancelToken(),
    });
    
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
};

export const analyzeEmail = async (emailText: string): Promise<AnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('email_text', emailText);
    
    const response = await api.post<AnalysisResponse>('/analyze/email', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      cancelToken: getCancelToken(),
    });
    
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
};

export const checkHealth = async (): Promise<{ status: string; version: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
};
