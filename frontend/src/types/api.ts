// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
  request_id?: string;
}

// Authentication Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserInfo {
  user_id: string;
  username: string;
}

// Market Data Types
export interface MarketDataResponse {
  symbol: string;
  bid_rate: string;
  ask_rate: string;
  spread: string;
  timestamp: string;
  source: string;
}

// Lending Offer Types
export interface LendingOffer {
  id?: string;
  symbol: string;
  amount: string;
  rate: string;
  period: number;
  status: string;
  daily_earnings?: string;
  created_at?: string;
}

export interface SubmitLendingOfferRequest {
  symbol: string;
  amount: number;
  rate?: number;
  period: number;
}

export interface SubmitLendingOfferResponse {
  offer_id: string;
  status: string;
  message: string;
}

// Portfolio Types
export interface PortfolioResponse {
  user_id: string;
  summary: {
    total_lent?: string;
    total_earned?: string;
    active_offers?: number;
  };
  active_positions: LendingOffer[];
  completed_positions?: LendingOffer[];
  performance_metrics?: {
    [key: string]: any;
  };
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp: string;
}

export interface MarketDataUpdate extends WebSocketMessage {
  type: 'market_data_update';
  symbol: string;
  data: {
    bid_rate: string;
    ask_rate: string;
    spread: string;
  };
}

export interface PortfolioUpdate extends WebSocketMessage {
  type: 'portfolio_update';
  data: PortfolioResponse;
}