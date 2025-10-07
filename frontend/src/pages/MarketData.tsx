import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Alert,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import { TrendingUp, Refresh, AttachMoney, MoneyOff, Wifi, WifiOff } from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { marketDataApi } from '../services/api';
import { useMarketDataWebSocket } from '../hooks/useWebSocket';
import type { MarketDataResponse, MarketDataUpdate } from '../types/api';

const POPULAR_SYMBOLS = ['fUSD', 'fBTC', 'fETH', 'fUST', 'fEUR', 'fGBP'];

export const MarketData: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedSymbol, setSelectedSymbol] = useState<string>('fUSD');
  const [wsUpdateMessage, setWsUpdateMessage] = useState<string>('');

  // Fetch available symbols
  const { data: symbols = [], isLoading: symbolsLoading } = useQuery({
    queryKey: ['market-symbols'],
    queryFn: marketDataApi.getSymbols,
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  // Fetch market data for selected symbol
  const {
    data: marketData,
    isLoading: marketLoading,
    error: marketError,
    refetch: refetchMarketData,
  } = useQuery({
    queryKey: ['market-data', selectedSymbol],
    queryFn: () => marketDataApi.getMarketData(selectedSymbol),
    refetchInterval: 30000, // Refresh every 30 seconds
    enabled: !!selectedSymbol,
  });

  // WebSocket integration for real-time updates
  const { state: wsState } = useMarketDataWebSocket(selectedSymbol, (update: MarketDataUpdate) => {
    // Update the cached data with real-time WebSocket data
    queryClient.setQueryData(['market-data', selectedSymbol], (oldData: MarketDataResponse | undefined) => {
      if (!oldData) return oldData;

      setWsUpdateMessage(`Real-time update received for ${selectedSymbol.replace('f', '')}`);
      setTimeout(() => setWsUpdateMessage(''), 3000);

      // Update the market data with WebSocket data
      return {
        ...oldData,
        bid_rate: update.data.bid_rate,
        ask_rate: update.data.ask_rate,
        timestamp: update.timestamp,
        source: 'websocket'
      };
    });
  });

  // Manual refresh function
  const handleRefresh = async () => {
    try {
      await marketDataApi.refreshMarketData(selectedSymbol);
      refetchMarketData();
    } catch (error) {
      console.error('Failed to refresh market data:', error);
    }
  };

  const formatRate = (rate: string) => {
    const numRate = parseFloat(rate);
    return (numRate * 100).toFixed(4);
  };

  const formatSpread = (spread: string) => {
    const numSpread = parseFloat(spread);
    return `${(numSpread * 100).toFixed(2)}%`;
  };

  const renderMarketCard = (data: MarketDataResponse) => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            {data.symbol.replace('f', '')} Lending Market
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={`Source: ${data.source}`}
              variant="outlined"
              size="small"
              color={data.source === 'api' ? 'success' : 'default'}
            />
            <Button
              startIcon={<Refresh />}
              onClick={handleRefresh}
              size="small"
              variant="outlined"
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3, mb: 3 }}>
          {/* Best Bid Rate (Lending Rate) */}
          <Box sx={{ flex: 1, textAlign: 'center', p: 2, border: 1, borderColor: 'success.main', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              <AttachMoney sx={{ color: 'success.main', mr: 1 }} />
              <Typography variant="h6" color="success.main">
                LEND Rate
              </Typography>
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main', mb: 1 }}>
              {formatRate(data.bid_rate)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Annual interest rate for lending
            </Typography>
          </Box>

          {/* Best Ask Rate (Borrowing Rate) */}
          <Box sx={{ flex: 1, textAlign: 'center', p: 2, border: 1, borderColor: 'error.main', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              <MoneyOff sx={{ color: 'error.main', mr: 1 }} />
              <Typography variant="h6" color="error.main">
                BORROW Rate
              </Typography>
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main', mb: 1 }}>
              {formatRate(data.ask_rate)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Annual interest rate for borrowing
            </Typography>
          </Box>

          {/* Spread */}
          <Box sx={{ flex: 1, textAlign: 'center', p: 2, border: 1, borderColor: 'warning.main', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              <TrendingUp sx={{ color: 'warning.main', mr: 1 }} />
              <Typography variant="h6" color="warning.main">
                Spread
              </Typography>
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main', mb: 1 }}>
              {formatSpread(data.spread)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Difference between lend/borrow rates
            </Typography>
          </Box>
        </Box>

        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {new Date(data.timestamp).toLocaleString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Market Data Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={wsState === 'connected' ? <Wifi /> : <WifiOff />}
              label={`WebSocket: ${wsState}`}
              color={wsState === 'connected' ? 'success' : wsState === 'connecting' ? 'warning' : 'error'}
              size="small"
              variant="outlined"
            />
          </Box>
        </Box>

        {/* Symbol Selection */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Select Trading Pair
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {(symbols.length > 0 ? symbols.slice(0, 10) : POPULAR_SYMBOLS).map((symbol) => (
              <Chip
                key={symbol}
                label={symbol.replace('f', '')}
                onClick={() => setSelectedSymbol(symbol)}
                variant={selectedSymbol === symbol ? 'filled' : 'outlined'}
                color={selectedSymbol === symbol ? 'primary' : 'default'}
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        </Paper>

        {/* Market Data Display */}
        {marketError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Failed to load market data. Please try again later.
          </Alert>
        )}

        {marketLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : marketData ? (
          renderMarketCard(marketData)
        ) : (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              No market data available
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please select a trading pair to view market data.
            </Typography>
          </Paper>
        )}

        {/* Lending Market Overview Table */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Lending Market Overview
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Real-time cryptocurrency lending rates and spreads across available markets
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Lend Rate</TableCell>
                  <TableCell align="right">Borrow Rate</TableCell>
                  <TableCell align="right">Spread</TableCell>
                  <TableCell align="center">Source</TableCell>
                  <TableCell align="center">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {symbolsLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress size={24} />
                    </TableCell>
                  </TableRow>
                ) : symbols.length > 0 ? (
                  symbols.slice(0, 10).map((symbol) => (
                    <TableRow
                      key={symbol}
                      hover
                      onClick={() => setSelectedSymbol(symbol)}
                      sx={{
                        cursor: 'pointer',
                        backgroundColor: selectedSymbol === symbol ? 'action.selected' : 'inherit'
                      }}
                    >
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {symbol.replace('f', '')}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {marketData && symbol === selectedSymbol ? (
                          <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 'medium' }}>
                            {formatRate(marketData.bid_rate)}%
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        {marketData && symbol === selectedSymbol ? (
                          <Typography variant="body2" sx={{ color: 'error.main', fontWeight: 'medium' }}>
                            {formatRate(marketData.ask_rate)}%
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        {marketData && symbol === selectedSymbol ? (
                          <Typography variant="body2" sx={{ color: 'warning.main', fontWeight: 'medium' }}>
                            {formatSpread(marketData.spread)}
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        {marketData && symbol === selectedSymbol ? (
                          <Chip
                            label={marketData.source}
                            size="small"
                            color={marketData.source === 'api' ? 'success' : 'default'}
                            variant="outlined"
                          />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={marketData && symbol === selectedSymbol ? 'Live' : 'Select'}
                          size="small"
                          color={marketData && symbol === selectedSymbol ? 'success' : 'default'}
                          variant={marketData && symbol === selectedSymbol ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary">
                        No market data available
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Market Information */}
          <Box sx={{ mt: 3, p: 2, backgroundColor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
              💡 Lending Market Information
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • <strong>Lend Rate (Bid)</strong>: The interest rate you earn by lending your cryptocurrency
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • <strong>Borrow Rate (Ask)</strong>: The interest rate you pay to borrow cryptocurrency
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <strong>Spread</strong>: The difference between lending and borrowing rates (market maker profit)
            </Typography>
          </Box>
        </Paper>
      </Box>

      {/* WebSocket Update Notification */}
      <Snackbar
        open={!!wsUpdateMessage}
        autoHideDuration={3000}
        onClose={() => setWsUpdateMessage('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setWsUpdateMessage('')} severity="info" sx={{ width: '100%' }}>
          {wsUpdateMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};