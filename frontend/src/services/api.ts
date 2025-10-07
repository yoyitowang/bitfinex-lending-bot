import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { ApiResponse, LoginRequest, LoginResponse, MarketDataResponse, SubmitLendingOfferRequest, SubmitLendingOfferResponse, PortfolioResponse, LendingOffer } from '../types/api';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Service Functions
export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<ApiResponse<LoginResponse>>('/api/v1/auth/login', credentials);
    return response.data.data!;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/v1/auth/logout');
  },

  getCurrentUser: async (): Promise<any> => {
    const response = await api.get<ApiResponse>('/api/v1/auth/me');
    return response.data.data;
  },
};

export const marketDataApi = {
  getSymbols: async (): Promise<string[]> => {
    const response = await api.get<ApiResponse<{ symbols: string[]; count: number }>>('/api/v1/market-data');
    return response.data.data!.symbols;
  },

  getMarketData: async (symbol: string): Promise<MarketDataResponse> => {
    const response = await api.get<ApiResponse<MarketDataResponse>>(`/api/v1/market-data/${symbol}`);
    return response.data.data!;
  },

  refreshMarketData: async (symbol: string): Promise<MarketDataResponse> => {
    const response = await api.post<ApiResponse<MarketDataResponse>>(`/api/v1/market-data/${symbol}/refresh`);
    return response.data.data!;
  },
};

export const lendingApi = {
  submitOffer: async (offer: SubmitLendingOfferRequest): Promise<SubmitLendingOfferResponse> => {
    const response = await api.post<ApiResponse<SubmitLendingOfferResponse>>('/api/v1/lending/offers', offer);
    return response.data.data!;
  },

  getActiveOffers: async (): Promise<LendingOffer[]> => {
    const response = await api.get<ApiResponse<{ offers: LendingOffer[]; count: number }>>('/api/v1/lending/offers');
    return response.data.data!.offers;
  },

  cancelOffer: async (offerId: string): Promise<void> => {
    await api.put(`/api/v1/lending/offers/${offerId}/cancel`);
  },
};

export const portfolioApi = {
  getPortfolio: async (includeCompleted: boolean = false): Promise<PortfolioResponse> => {
    const response = await api.get<ApiResponse<PortfolioResponse>>(`/api/v1/portfolio?include_completed=${includeCompleted}`);
    return response.data.data!;
  },
};

export const healthApi = {
  checkHealth: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get<{ status: string; service: string }>('/health');
    return response.data;
  },
};

export default api;