import axios, { AxiosError } from 'axios';
import type { ApiError, CompressionResult } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const compressImage = async (
  file: File,
  quality: number = 85,
  maxWidth?: number,
  maxHeight?: number,
  outputFormat?: string
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  const params = new URLSearchParams();
  params.append('quality', quality.toString());
  if (maxWidth) params.append('max_width', maxWidth.toString());
  if (maxHeight) params.append('max_height', maxHeight.toString());
  if (outputFormat) params.append('output_format', outputFormat);

  try {
    const response = await api.post(
      `/api/compression/compress?${params.toString()}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Compression failed');
    }
    throw error;
  }
};

export const downloadCompressedImage = (filename: string): string => {
  return `${API_URL}/api/compression/download/${filename}`;
};

export const compressVideo = async (
  file: File,
  quality: 'low' | 'medium' | 'high' = 'medium',
  maxWidth?: number,
  outputFormat: string = 'mp4'
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  const params = new URLSearchParams();
  params.append('quality', quality);
  if (maxWidth) params.append('max_width', maxWidth.toString());
  params.append('output_format', outputFormat);

  try {
    const response = await api.post(
      `/api/compression/compress-video?${params.toString()}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Video compression failed');
    }
    throw error;
  }
};

export const deleteCompressedImage = async (filename: string): Promise<void> => {
  try {
    await api.delete(`/api/compression/delete/${filename}`);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Failed to delete file');
    }
    throw error;
  }
};

// Speech API functions
export const getSupportedLanguages = async (): Promise<{ code: string; name: string }[]> => {
  try {
    const response = await api.get('/api/speech/languages');
    if (response.data.success) {
      return response.data.languages;
    }
    return [];
  } catch (error) {
    console.error('Failed to load languages:', error);
    return [];
  }
};

export const transcribeAudio = async (file: File): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/api/speech/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Transcription failed');
    }
    throw error;
  }
};

export const synthesizeSpeech = async (
  text: string,
  language: string = 'en',
  slow: boolean = false,
  voice?: string,
  rate: number = 1.0,
  pitch: number = 1.0,
  style: string = 'default'
): Promise<Blob> => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('language', language);
  formData.append('slow', slow.toString());
  if (voice) {
    formData.append('voice', voice);
  }
  formData.append('rate', rate.toString());
  formData.append('pitch', pitch.toString());
  formData.append('style', style);

  try {
    const response = await api.post('/api/speech/synthesize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Synthesis failed');
    }
    throw error;
  }
};

export const getAvailableVoices = async (): Promise<any> => {
  try {
    const response = await api.get('/api/speech/voices');
    if (response.data.success) {
      return response.data.voices;
    }
    return [];
  } catch (error) {
    console.error('Failed to load voices:', error);
    return [];
  }
};

export const getAvailableStyles = async (): Promise<any> => {
  try {
    const response = await api.get('/api/speech/styles');
    if (response.data.success) {
      return response.data.styles;
    }
    return [];
  } catch (error) {
    console.error('Failed to load styles:', error);
    return [];
  }
};

export const extractTextFromFile = async (file: File): Promise<{ success: boolean; text: string; length: number }> => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/api/speech/extract-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    if (response.data.success) {
      return response.data;
    }
    throw new Error('Failed to extract text from file');
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Failed to extract text from file');
    }
    throw error;
  }
};

// Translation API functions
export const getSupportedTranslationLanguages = async (): Promise<{ code: string; name: string }[]> => {
  try {
    const response = await api.get('/api/translation/languages');
    if (response.data.success) {
      return response.data.languages;
    }
    return [];
  } catch (error) {
    console.error('Failed to load translation languages:', error);
    return [];
  }
};

export const translateText = async (
  text: string,
  sourceLang: string = 'auto',
  targetLang: string = 'en'
): Promise<any> => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('source_lang', sourceLang);
  formData.append('target_lang', targetLang);

  try {
    const response = await api.post('/api/translation/translate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Translation failed');
    }
    throw error;
  }
};

// AI Detection API functions
export const analyzeAIContent = async (text: string): Promise<any> => {
  const formData = new FormData();
  formData.append('text', text);

  try {
    const response = await api.post('/api/ai-detection/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'AI detection failed');
    }
    throw error;
  }
};

// OCR API functions
export const extractTextFromImage = async (file: File, language: string = 'eng'): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);

  try {
    const response = await api.post('/api/ocr/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'OCR extraction failed');
    }
    throw error;
  }
};

export const translateImageText = async (
  file: File,
  sourceLang: string,
  targetLang: string
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post(
      `/api/ocr/translate-image?source_lang=${sourceLang}&target_lang=${targetLang}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      throw new Error(axiosError.response?.data?.detail || 'Image translation failed');
    }
    throw error;
  }
};

export const getSupportedOCRLanguages = async (): Promise<{ code: string; name: string }[]> => {
  try {
    const response = await api.get('/api/ocr/supported-languages');
    if (response.data.success) {
      return response.data.languages;
    }
    return [];
  } catch (error) {
    console.error('Failed to load OCR languages:', error);
    return [];
  }
};

export default api;
