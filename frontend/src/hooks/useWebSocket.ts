import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './useAuth';
import type { WebSocketMessage, MarketDataUpdate, PortfolioUpdate } from '../types/api';

// WebSocket connection states
export type WebSocketState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onStateChange?: (state: WebSocketState) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onStateChange,
  reconnectInterval = 5000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions) => {
  const { user } = useAuth();
  const [state, setState] = useState<WebSocketState>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | undefined>(undefined);
  const reconnectAttemptsRef = useRef(0);

  const updateState = useCallback((newState: WebSocketState) => {
    setState(newState);
    onStateChange?.(newState);
  }, [onStateChange]);

  const connect = useCallback(() => {
    if (!user) return;

    updateState('connecting');

    try {
      // Add JWT token to WebSocket URL
      const token = localStorage.getItem('auth_token');
      const wsUrl = token ? `${url}?token=${token}` : url;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected:', url);
        updateState('connected');
        reconnectAttemptsRef.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', url, event.code, event.reason);
        updateState('disconnected');

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateState('error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      updateState('error');
    }
  }, [url, user, updateState, reconnectInterval, maxReconnectAttempts, onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Component unmounting');
      wsRef.current = null;
    }

    updateState('disconnected');
  }, [updateState]);

  const send = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }, []);

  // Connect when user is available
  useEffect(() => {
    if (user) {
      connect();
    } else {
      disconnect();
    }

    return disconnect;
  }, [user, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return disconnect;
  }, [disconnect]);

  return {
    state,
    send,
    connect,
    disconnect,
    isConnected: state === 'connected',
    isConnecting: state === 'connecting',
  };
};

// Specific hooks for different WebSocket endpoints

export const useMarketDataWebSocket = (symbol: string, onUpdate?: (update: MarketDataUpdate) => void) => {
  const [lastUpdate, setLastUpdate] = useState<MarketDataUpdate | null>(null);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'market_data_update' && (message as MarketDataUpdate).symbol === symbol) {
      const update = message as MarketDataUpdate;
      setLastUpdate(update);
      onUpdate?.(update);
    }
  }, [symbol, onUpdate]);

  const ws = useWebSocket({
    url: `ws://localhost:8000/api/v1/ws/market-data/${symbol}`,
    onMessage: handleMessage,
  });

  return {
    ...ws,
    lastUpdate,
  };
};

export const usePortfolioWebSocket = (onUpdate?: (update: PortfolioUpdate) => void) => {
  const [lastUpdate, setLastUpdate] = useState<PortfolioUpdate | null>(null);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'portfolio_update') {
      const update = message as PortfolioUpdate;
      setLastUpdate(update);
      onUpdate?.(update);
    }
  }, [onUpdate]);

  const ws = useWebSocket({
    url: 'ws://localhost:8000/api/v1/ws/portfolio',
    onMessage: handleMessage,
  });

  return {
    ...ws,
    lastUpdate,
  };
};