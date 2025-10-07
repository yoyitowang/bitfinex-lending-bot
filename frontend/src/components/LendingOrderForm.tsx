import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  Card,
  CardContent,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { lendingApi, marketDataApi } from '../services/api';
import type { SubmitLendingOfferRequest } from '../types/api';

interface LendingOrderFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

const AVAILABLE_SYMBOLS = ['fUSD', 'fBTC', 'fETH', 'fUST', 'fEUR', 'fGBP'];
const PERIOD_OPTIONS = [
  { value: 2, label: '2 days' },
  { value: 7, label: '1 week' },
  { value: 14, label: '2 weeks' },
  { value: 30, label: '1 month' },
  { value: 60, label: '2 months' },
  { value: 90, label: '3 months' },
  { value: 120, label: '4 months' },
  { value: 180, label: '6 months' },
  { value: 365, label: '1 year' },
];

export const LendingOrderForm: React.FC<LendingOrderFormProps> = ({
  onSuccess,
  onCancel
}) => {
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState<SubmitLendingOfferRequest>({
    symbol: 'fUSD',
    amount: 1000,
    rate: undefined,
    period: 30,
  });

  const [useCustomRate, setUseCustomRate] = useState(false);

  // Fetch market data for rate suggestions
  const { data: marketData, isLoading: marketLoading } = useQuery({
    queryKey: ['market-data', formData.symbol],
    queryFn: () => marketDataApi.getMarketData(formData.symbol),
    enabled: !!formData.symbol,
  });

  // Submit lending offer mutation
  const submitMutation = useMutation({
    mutationFn: lendingApi.submitOffer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      queryClient.invalidateQueries({ queryKey: ['active-offers'] });
      onSuccess?.();
    },
  });

  // Calculate suggested rates based on market data
  const suggestedRates = React.useMemo(() => {
    if (!marketData) return null;

    const bidRate = parseFloat(marketData.bid_rate);
    return {
      conservative: bidRate * 0.8, // 80% of current bid rate
      market: bidRate,             // Current market bid rate
      aggressive: bidRate * 1.2,   // 120% of current bid rate
    };
  }, [marketData]);

  // Set default rate when market data loads
  useEffect(() => {
    if (suggestedRates && !useCustomRate && !formData.rate) {
      setFormData(prev => ({ ...prev, rate: suggestedRates.conservative }));
    }
  }, [suggestedRates, useCustomRate, formData.rate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.amount || formData.amount <= 0) {
      return;
    }

    if (!formData.rate || formData.rate <= 0) {
      return;
    }

    try {
      await submitMutation.mutateAsync(formData);
    } catch (error) {
      console.error('Failed to submit lending offer:', error);
    }
  };

  const handleRatePreset = (preset: 'conservative' | 'market' | 'aggressive') => {
    if (suggestedRates) {
      setFormData(prev => ({ ...prev, rate: suggestedRates[preset] }));
      setUseCustomRate(false);
    }
  };

  const handleCustomRateChange = (rate: number) => {
    setFormData(prev => ({ ...prev, rate }));
    setUseCustomRate(true);
  };

  const calculateEstimatedEarnings = () => {
    if (!formData.amount || !formData.rate || !formData.period) return 0;

    const dailyRate = formData.rate / 100 / 365; // Convert annual percentage to daily decimal
    const dailyEarnings = formData.amount * dailyRate;
    return dailyEarnings * formData.period;
  };

  const estimatedEarnings = calculateEstimatedEarnings();

  if (marketLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Create Lending Offer
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Lend your cryptocurrency and earn interest. Set your terms and submit your offer to the market.
      </Typography>

      <Box component="form" onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3, mb: 3 }}>
          {/* Symbol Selection */}
          <Box sx={{ flex: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Trading Pair</InputLabel>
              <Select
                value={formData.symbol}
                label="Trading Pair"
                onChange={(e) => setFormData(prev => ({ ...prev, symbol: e.target.value }))}
              >
                {AVAILABLE_SYMBOLS.map((symbol) => (
                  <MenuItem key={symbol} value={symbol}>
                    {symbol.replace('f', '')}/USD
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Period Selection */}
          <Box sx={{ flex: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Lending Period</InputLabel>
              <Select
                value={formData.period}
                label="Lending Period"
                onChange={(e) => setFormData(prev => ({ ...prev, period: Number(e.target.value) }))}
              >
                {PERIOD_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Box>

        {/* Amount Input */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Amount to Lend"
            type="number"
            value={formData.amount}
            onChange={(e) => setFormData(prev => ({ ...prev, amount: Number(e.target.value) }))}
            required
            inputProps={{ min: 50, step: 0.01 }}
            helperText={`Minimum lending amount is 50 ${formData.symbol.replace('f', '')}`}
          />
        </Box>

        {/* Rate Selection */}
        <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Interest Rate
            </Typography>

            {/* Market Rate Information */}
            {marketData && (
              <Card sx={{ mb: 2, bgcolor: 'background.paper' }}>
                <CardContent sx={{ py: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Current Market Rates
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip
                      label={`Current: ${(parseFloat(marketData.bid_rate) * 100).toFixed(2)}%`}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={`Borrow: ${(parseFloat(marketData.ask_rate) * 100).toFixed(2)}%`}
                      size="small"
                      variant="outlined"
                      color="warning"
                    />
                  </Box>
                </CardContent>
              </Card>
            )}

            {/* Rate Presets */}
            {suggestedRates && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Suggested Rates:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                  <Button
                    size="small"
                    variant={!useCustomRate && formData.rate === suggestedRates.conservative ? "contained" : "outlined"}
                    onClick={() => handleRatePreset('conservative')}
                  >
                    Conservative: {(suggestedRates.conservative * 100).toFixed(2)}%
                  </Button>
                  <Button
                    size="small"
                    variant={!useCustomRate && formData.rate === suggestedRates.market ? "contained" : "outlined"}
                    onClick={() => handleRatePreset('market')}
                  >
                    Market: {(suggestedRates.market * 100).toFixed(2)}%
                  </Button>
                  <Button
                    size="small"
                    variant={!useCustomRate && formData.rate === suggestedRates.aggressive ? "contained" : "outlined"}
                    onClick={() => handleRatePreset('aggressive')}
                  >
                    Aggressive: {(suggestedRates.aggressive * 100).toFixed(2)}%
                  </Button>
                  <Button
                    size="small"
                    variant={useCustomRate ? "contained" : "outlined"}
                    onClick={() => setUseCustomRate(true)}
                  >
                    Custom Rate
                  </Button>
                </Box>
              </Box>
            )}

            {/* Custom Rate Input */}
            <TextField
              fullWidth
              label="Annual Interest Rate (%)"
              type="number"
              value={formData.rate || ''}
              onChange={(e) => handleCustomRateChange(Number(e.target.value))}
              required
              inputProps={{ min: 0.01, max: 100, step: 0.01 }}
              helperText="Enter your desired annual interest rate"
            />
          </Box>

          {/* Earnings Estimate */}
          {formData.amount && formData.rate && formData.period && (
            <Box sx={{ mb: 3 }}>
              <Card sx={{ bgcolor: 'success.light', color: 'success.contrastText' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    📈 Estimated Earnings
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    ${estimatedEarnings.toFixed(2)}
                  </Typography>
                  <Typography variant="body2">
                    For lending ${formData.amount} {formData.symbol.replace('f', '')} at {(formData.rate * 100).toFixed(2)}% for {formData.period} days
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}

          {/* Error Display */}
          {submitMutation.error && (
            <Box sx={{ mb: 3 }}>
              <Alert severity="error">
                Failed to submit lending offer: {submitMutation.error.message}
              </Alert>
            </Box>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            {onCancel && (
              <Button
                variant="outlined"
                onClick={onCancel}
                disabled={submitMutation.isPending}
              >
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={submitMutation.isPending || !formData.amount || !formData.rate}
            >
              {submitMutation.isPending ? <CircularProgress size={24} /> : 'Submit Lending Offer'}
            </Button>
          </Box>
      </Box>

      {/* Success Message */}
      {submitMutation.isSuccess && (
        <Alert severity="success" sx={{ mt: 2 }}>
          ✅ Lending offer submitted successfully! Check your portfolio to monitor its status.
        </Alert>
      )}
    </Paper>
  );
};