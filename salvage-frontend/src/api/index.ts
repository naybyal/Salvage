import axios, { AxiosInstance } from 'axios';
import {JWTTokens, SaveFileRequest, TranspileResponse} from '../types/index';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor
api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('access');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh');
        const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/token/refresh/`, {
          refresh: refreshToken
        });

        const { access } = response.data;
        localStorage.setItem('access', access);
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (err) {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export const registerUser = async (credentials: AuthCredentials): Promise<void> => {
  await api.post('/api/signup/', credentials);
};

export const loginUser = async (credentials: AuthCredentials): Promise<JWTTokens> => {
  const response = await api.post('/api/token/', credentials);
  return response.data;
};

export const getFiles = async (): Promise<File[]> => {
  const response = await api.get('/api/files/');
  return response.data;
};

export const saveFile = async (fileData: SaveFileRequest): Promise<File> => {
  const response = await api.post('/api/files/', fileData);
  return response.data;
};

export const deleteFile = async (fileId: number): Promise<void> => {
  await api.delete(`/api/files/${fileId}/`);
};

export const transpileCode = async (code: string): Promise<string> => {
  const response = await api.post<TranspileResponse>('/transpiler/transpile/', { code });
  return response.data.rust_code;
};