import axios, { AxiosInstance } from 'axios';
import { JWTTokens } from '../types/index';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

export const transpileCode = async (code: string): Promise<string> => {
  const response = await api.post<TranspileResponse>('/transpiler/transpile/', { code });
  return response.data.rust_code;
};