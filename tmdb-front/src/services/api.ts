import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';



interface ApiConfig {
  apiBaseURL: string;
  apiTimeout: number;
}

const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, '');

const getConfig = (): ApiConfig => {
  return {
    apiBaseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    apiTimeout: import.meta.env.VITE_API_TIMEOUT ? parseInt(import.meta.env.VITE_API_TIMEOUT) : 10000,
  };
};

const config = getConfig();


export const api: AxiosInstance = axios.create({
  baseURL: config.apiBaseURL,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, 
});


export const tmdbApi: AxiosInstance = axios.create({
  baseURL: `${trimTrailingSlash(config.apiBaseURL)}/tmdb`,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});


api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config;
  },
  (error: unknown) => {
    return Promise.reject(error);
  }
);


api.interceptors.response.use(
  (response: any) => response,
  (error: any) => {

    return Promise.reject(error);
  }
);


export default api;
