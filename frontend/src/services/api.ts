/**
 * API service for communicating with the backend.
 */
import axios, { AxiosError } from 'axios';
import { AnalysisResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
const handleError = (error: AxiosError): never => {
  if (error.response) {
    throw new Error(error.response.data?.detail || 'An error occurred');
  } else if (error.request) {
    throw new Error('No response from server. Please check your connection.');
  } else {
    throw new Error('Request failed. Please try again.');
  }
};

export const analyzeImage = async (file: File, isLive: boolean = false): Promise<AnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_live', isLive.toString());
    
    const response = await api.post<AnalysisResponse>('/analyze/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
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
