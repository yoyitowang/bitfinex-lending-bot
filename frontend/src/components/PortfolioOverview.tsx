import React from 'react';
import {
  Box,
  Paper,
  Typography,
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
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  Schedule,
  CheckCircle,
  Cancel,
  Refresh,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { portfolioApi } from '../services/api';
import { usePortfolioWebSocket } from '../hooks/useWebSocket';
import type { LendingOffer, PortfolioUpdate } from '../types/api';

interface PortfolioOverviewProps {
  onRefresh?: () => void;
}

export const PortfolioOverview: React.FC<PortfolioOverviewProps> = ({ onRefresh }) => {
  const queryClient = useQueryClient();

  // WebSocket integration for real-time portfolio updates
  const { state: wsState } = usePortfolioWebSocket((update) => {
    // Update portfolio data with real-time WebSocket data
    queryClient.setQueryData(['portfolio'], update.data);
    onRefresh?.();
  });

  const {
    data: portfolio,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['portfolio'],
    queryFn: () => portfolioApi.getPortfolio(true),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const handleRefresh = async () => {
    await refetch();
    onRefresh?.();
  };

  const formatCurrency = (amount: string | number) => {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'completed':
        return 'primary';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string): React.ReactElement | undefined => {
    switch (status.toLowerCase()) {
      case 'active':
        return <Schedule />;
      case 'completed':
        return <CheckCircle />;
      case 'cancelled':
        return <Cancel />;
      default:
        return undefined;
    }
  };

  const calculateProgress = (offer: LendingOffer) => {
    if (!offer.created_at) return 0;

    const createdDate = new Date(offer.created_at);
    const currentDate = new Date();
    const periodDays = offer.period;
    const elapsedDays = (currentDate.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24);

    return Math.min((elapsedDays / periodDays) * 100, 100);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        Failed to load portfolio data. Please try again later.
      </Alert>
    );
  }

  if (!portfolio) {
    return (
      <Alert severity="info" sx={{ mb: 3 }}>
        No portfolio data available.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Portfolio Summary Cards */}
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, mb: 4 }}>
        <Card sx={{ flex: 1, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <AccountBalance sx={{ mr: 1 }} />
              <Typography variant="h6">Total Lent</Typography>
            </Box>
            <Typography variant="h4">
              {formatCurrency(portfolio.summary?.total_lent || '0')}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Active lending positions
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUp sx={{ mr: 1 }} />
              <Typography variant="h6">Total Earned</Typography>
            </Box>
            <Typography variant="h4">
              {formatCurrency(portfolio.summary?.total_earned || '0')}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Interest earned to date
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1, background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Schedule sx={{ mr: 1 }} />
              <Typography variant="h6">Active Offers</Typography>
            </Box>
            <Typography variant="h4">
              {portfolio.summary?.active_offers || 0}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Currently lending offers
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Active Positions */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Active Lending Positions</Typography>
          <Button
            startIcon={<Refresh />}
            onClick={handleRefresh}
            variant="outlined"
            size="small"
          >
            Refresh
          </Button>
        </Box>

        {portfolio.active_positions && portfolio.active_positions.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell align="right">Rate</TableCell>
                  <TableCell align="right">Period</TableCell>
                  <TableCell align="right">Created</TableCell>
                  <TableCell align="center">Progress</TableCell>
                  <TableCell align="center">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {portfolio.active_positions.map((offer: LendingOffer) => (
                  <TableRow key={offer.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {offer.symbol.replace('f', '')}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(offer.amount)}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${(parseFloat(offer.rate) * 100).toFixed(2)}%`}
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {offer.period} days
                    </TableCell>
                    <TableCell align="right">
                      {offer.created_at ? formatDate(offer.created_at) : '-'}
                    </TableCell>
                    <TableCell align="center" sx={{ minWidth: 120 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: 'column', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={calculateProgress(offer)}
                          sx={{ width: '100%', height: 8, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {Math.round(calculateProgress(offer))}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={offer.status}
                        size="small"
                        color={getStatusColor(offer.status)}
                        icon={getStatusIcon(offer.status)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Active Positions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Create lending offers to start earning interest on your cryptocurrency holdings.
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Completed Positions */}
      {portfolio.completed_positions && portfolio.completed_positions.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Completed Positions
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell align="right">Rate</TableCell>
                  <TableCell align="right">Earnings</TableCell>
                  <TableCell align="right">Completed</TableCell>
                  <TableCell align="center">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {portfolio.completed_positions.map((offer: LendingOffer) => (
                  <TableRow key={offer.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {offer.symbol.replace('f', '')}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(offer.amount)}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${(parseFloat(offer.rate) * 100).toFixed(2)}%`}
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 'medium' }}>
                        {offer.daily_earnings ? formatCurrency(offer.daily_earnings) : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="text.secondary">
                        -
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label="Completed"
                        size="small"
                        color="primary"
                        icon={<CheckCircle />}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Performance Metrics */}
      {portfolio.performance_metrics && Object.keys(portfolio.performance_metrics).length > 0 && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Performance Metrics
          </Typography>

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {Object.entries(portfolio.performance_metrics).map(([key, value]) => (
              <Box key={key} sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(33.333% - 11px)' } }}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                    <Typography variant="h6">
                      {typeof value === 'number' ? value.toLocaleString() : String(value)}
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};