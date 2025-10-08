import React, { useState } from 'react';
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
      <CardContent sx={{ p: { xs: 2, md: 3 } }}>
        <Box sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          justifyContent: 'space-between',
          alignItems: { xs: 'flex-start', sm: 'center' },
          gap: { xs: 2, sm: 0 },
          mb: 2
        }}>
          <Typography
            variant="h5"
            component="h2"
            sx={{
              fontSize: { xs: '1.5rem', md: '1.5rem' },
              mb: { xs: 1, sm: 0 }
            }}
          >
            {data.symbol.replace('f', '')} Lending Market
          </Typography>
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            flexWrap: 'wrap'
          }}>
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
              sx={{ minWidth: 'auto' }}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <Box sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
          gap: 2,
          mb: 3
        }}>
          {/* Best Bid Rate (Lending Rate) */}
          <Box sx={{
            textAlign: 'center',
            p: { xs: 1.5, md: 2 },
            border: 1,
            borderColor: 'success.main',
            borderRadius: 2,
            minHeight: { xs: '100px', md: '120px' }
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              <AttachMoney sx={{ color: 'success.main', mr: 1, fontSize: { xs: '1.2rem', md: '1.5rem' } }} />
              <Typography
                variant="h6"
                color="success.main"
                sx={{ fontSize: { xs: '1rem', md: '1.25rem' } }}
              >
                LEND Rate
              </Typography>
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 'bold',
                color: 'success.main',
                mb: 1,
                fontSize: { xs: '1.5rem', md: '2.125rem' }
              }}
            >
              {formatRate(data.bid_rate)}%
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontSize: { xs: '0.75rem', md: '0.875rem' } }}
            >
              Annual interest rate for lending
            </Typography>
          </Box>

          {/* Best Ask Rate (Borrowing Rate) */}
          <Box sx={{
            textAlign: 'center',
            p: { xs: 1.5, md: 2 },
            border: 1,
            borderColor: 'error.main',
            borderRadius: 2,
            minHeight: { xs: '100px', md: '120px' }
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              <MoneyOff sx={{ color: 'error.main', mr: 1, fontSize: { xs: '1.2rem', md: '1.5rem' } }} />
              <Typography
                variant="h6"
                color="error.main"
                sx={{ fontSize: { xs: '1rem', md: '1.25rem' } }}
              >
                BORROW Rate
              </Typography>
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 'bold',
                color: 'error.main',
                mb: 1,
                fontSize: { xs: '1.5rem', md: '2.125rem' }
              }}
            >
              {formatRate(data.ask_rate)}%
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontSize: { xs: '0.75rem', md: '0.875rem' } }}
            >
              Annual interest rate for borrowing
            </Typography>
          </Box>

          {/* Spread */}
          <Box sx={{
            textAlign: 'center',
            p: { xs: 1.5, md: 2 },
            border: 1,
            borderColor: 'warning.main',
            borderRadius: 2,
            minHeight: { xs: '100px', md: '120px' }
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              <TrendingUp sx={{ color: 'warning.main', mr: 1, fontSize: { xs: '1.2rem', md: '1.5rem' } }} />
              <Typography
                variant="h6"
                color="warning.main"
                sx={{ fontSize: { xs: '1rem', md: '1.25rem' } }}
              >
                Spread
              </Typography>
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 'bold',
                color: 'warning.main',
                mb: 1,
                fontSize: { xs: '1.5rem', md: '2.125rem' }
              }}
            >
              {formatSpread(data.spread)}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontSize: { xs: '0.75rem', md: '0.875rem' } }}
            >
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
      <Box sx={{ my: { xs: 2, md: 4 } }}>
        <Box sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          justifyContent: 'space-between',
          alignItems: { xs: 'flex-start', sm: 'center' },
          gap: { xs: 2, sm: 0 },
          mb: 2
        }}>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontSize: { xs: '2rem', sm: '2.125rem', md: '3rem' }
            }}
            gutterBottom
          >
            Market Data Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={wsState === 'connected' ? <Wifi /> : <WifiOff />}
              label={`WebSocket: ${wsState}`}
              color={wsState === 'connected' ? 'success' : wsState === 'connecting' ? 'warning' : 'error'}
              size="small"
              variant="outlined"
              sx={{
                '& .MuiChip-label': {
                  display: { xs: 'none', sm: 'inline' }
                },
                '& .MuiChip-icon': {
                  marginRight: { xs: 0, sm: 1 }
                }
              }}
            />
          </Box>
        </Box>

        {/* Symbol Selection */}
        <Paper sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Select Trading Pair
          </Typography>
          <Box sx={{
            display: 'flex',
            gap: 1,
            flexWrap: 'wrap',
            '& .MuiChip-root': {
              mb: { xs: 1, sm: 0 }
            }
          }}>
            {(symbols.length > 0 ? symbols.slice(0, 10) : POPULAR_SYMBOLS).map((symbol) => (
              <Chip
                key={symbol}
                label={symbol.replace('f', '')}
                onClick={() => setSelectedSymbol(symbol)}
                variant={selectedSymbol === symbol ? 'filled' : 'outlined'}
                color={selectedSymbol === symbol ? 'primary' : 'default'}
                size="small"
                sx={{
                  cursor: 'pointer',
                  minWidth: { xs: '60px', sm: 'auto' }
                }}
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
        <Paper sx={{ p: { xs: 2, md: 3 } }}>
          <Typography
            variant="h6"
            gutterBottom
            sx={{ fontSize: { xs: '1.1rem', md: '1.25rem' } }}
          >
            Lending Market Overview
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 2, fontSize: { xs: '0.875rem', md: '0.875rem' } }}
          >
            Real-time cryptocurrency lending rates and spreads across available markets
          </Typography>

          <TableContainer sx={{
            maxWidth: '100%',
            overflowX: 'auto',
            '& .MuiTable-root': {
              minWidth: { xs: '600px', md: '100%' }
            }
          }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', fontSize: { xs: '0.875rem', md: '0.875rem' } }}>
                    Symbol
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: { xs: '0.875rem', md: '0.875rem' } }}>
                    Lend Rate
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: { xs: '0.875rem', md: '0.875rem' } }}>
                    Borrow Rate
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: { xs: '0.875rem', md: '0.875rem' } }}>
                    Spread
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 'bold', fontSize: { xs: '0.875rem', md: '0.875rem' } }}>
                    Source
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 'bold', fontSize: { xs: '0.875rem', md: '0.875rem' } }}>
                    Status
                  </TableCell>
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