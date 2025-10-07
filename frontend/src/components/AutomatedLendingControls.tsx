import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Divider,
  Slider,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Analytics,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { lendingApi } from '../services/api';
import type { AutomatedLendingRequest } from '../types/api';

interface AutomatedLendingControlsProps {
  onExecute?: (result: any) => void;
}

export const AutomatedLendingControls: React.FC<AutomatedLendingControlsProps> = ({ onExecute }) => {
  const queryClient = useQueryClient();
  const [selectedSymbol, setSelectedSymbol] = useState<string>('USD');
  const [totalAmount, setTotalAmount] = useState<string>('1000');
  const [period, setPeriod] = useState<number>(30);
  const [rateMin, setRateMin] = useState<string>('');
  const [rateMax, setRateMax] = useState<string>('');
  const [maxOrders, setMaxOrders] = useState<number>(10);
  const [cancelExisting, setCancelExisting] = useState<boolean>(false);
  const [useAllBalance, setUseAllBalance] = useState<boolean>(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState<boolean>(false);

  // Fetch automated lending analysis
  const {
    data: analysis,
    isLoading: analysisLoading,
    refetch: refetchAnalysis,
  } = useQuery({
    queryKey: ['automated-analysis', selectedSymbol],
    queryFn: () => lendingApi.getAutomatedAnalysis(selectedSymbol),
    enabled: !!selectedSymbol,
  });

  // Fetch lending conditions check
  const {
    data: conditionsCheck,
    isLoading: conditionsLoading,
    refetch: refetchConditions,
  } = useQuery({
    queryKey: ['automated-check', selectedSymbol, period],
    queryFn: () => lendingApi.checkAutomatedConditions(selectedSymbol, period),
    enabled: !!selectedSymbol && !!period,
  });

  // Execute automated lending mutation
  const executeMutation = useMutation({
    mutationFn: (params: AutomatedLendingRequest) => lendingApi.executeAutomatedLending(params),
    onSuccess: (result) => {
      setConfirmDialogOpen(false);
      onExecute?.(result);
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      queryClient.invalidateQueries({ queryKey: ['lending-offers'] });
    },
  });

  const handleExecute = () => {
    const params: AutomatedLendingRequest = {
      symbol: selectedSymbol,
      total_amount: parseFloat(totalAmount),
      period,
      rate_min: rateMin ? parseFloat(rateMin) : undefined,
      rate_max: rateMax ? parseFloat(rateMax) : undefined,
      max_orders: maxOrders,
      cancel_existing: cancelExisting,
      use_all_balance: useAllBalance,
    };

    executeMutation.mutate(params);
  };

  const getConditionStatus = () => {
    if (!conditionsCheck) return { status: 'unknown', icon: null, color: 'default' as const };

    const shouldLend = conditionsCheck.should_lend;
    if (shouldLend) {
      return { status: 'met', icon: <CheckCircle />, color: 'success' as const };
    } else {
      return { status: 'not-met', icon: <Error />, color: 'error' as const };
    }
  };

  const conditionStatus = getConditionStatus();

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Analytics sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Automated Lending Controls</Typography>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Configure and execute automated lending strategies based on real-time market analysis.
          The system will automatically determine optimal lending parameters when conditions are met.
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Symbol Selection */}
          <Box>
            <TextField
              fullWidth
              label="Currency Symbol"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              select
              SelectProps={{ native: true }}
            >
              <option value="USD">USD</option>
              <option value="BTC">BTC</option>
              <option value="ETH">ETH</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </TextField>
          </Box>

          {/* Period Selection */}
          <Box>
            <TextField
              fullWidth
              label="Lending Period (Days)"
              value={period}
              onChange={(e) => setPeriod(parseInt(e.target.value))}
              select
              SelectProps={{ native: true }}
            >
              <option value={2}>2 Days</option>
              <option value={30}>30 Days</option>
            </TextField>
          </Box>

          {/* Total Amount */}
          <Box>
            <TextField
              fullWidth
              label="Total Amount"
              type="number"
              value={totalAmount}
              onChange={(e) => setTotalAmount(e.target.value)}
              disabled={useAllBalance}
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
              }}
            />
          </Box>

          {/* Max Orders */}
          <Box>
            <Typography gutterBottom>Max Orders: {maxOrders}</Typography>
            <Slider
              value={maxOrders}
              onChange={(_, value) => setMaxOrders(value as number)}
              min={1}
              max={20}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Box>

          {/* Rate Range */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Minimum Rate (%)"
              type="number"
              value={rateMin}
              onChange={(e) => setRateMin(e.target.value)}
              InputProps={{ inputProps: { min: 0, step: 0.01 } }}
            />
            <TextField
              fullWidth
              label="Maximum Rate (%)"
              type="number"
              value={rateMax}
              onChange={(e) => setRateMax(e.target.value)}
              InputProps={{ inputProps: { min: 0, step: 0.01 } }}
            />
          </Box>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Options */}
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={useAllBalance}
                onChange={(e) => setUseAllBalance(e.target.checked)}
              />
            }
            label="Use all available balance"
          />

          <FormControlLabel
            control={
              <Switch
                checked={cancelExisting}
                onChange={(e) => setCancelExisting(e.target.checked)}
              />
            }
            label="Cancel existing offers first"
          />
        </Box>

        {/* Analysis Section */}
        {analysis && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Analysis for {selectedSymbol}
              </Typography>

              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                <Chip
                  label={`Avg Rate: ${analysis.average_rate_30d?.toFixed(4)}%`}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`Volatility: ${analysis.volatility_30d?.toFixed(2)}%`}
                  color="warning"
                  variant="outlined"
                />
                <Chip
                  label={`High Yield Opp: ${analysis.high_yield_opportunities || 0}`}
                  color="success"
                  variant="outlined"
                />
              </Box>

              {analysis.recommendations && (
                <Typography variant="body2" color="text.secondary">
                  {analysis.recommendations}
                </Typography>
              )}
            </CardContent>
          </Card>
        )}

        {/* Conditions Check */}
        {conditionsCheck && (
          <Alert
            severity={conditionStatus.status === 'met' ? 'success' : 'warning'}
            icon={conditionStatus.icon}
            sx={{ mb: 3 }}
          >
            <Typography variant="body2">
              Automated lending conditions: <strong>{conditionStatus.status === 'met' ? 'MET' : 'NOT MET'}</strong>
            </Typography>
            {conditionsCheck.confidence && (
              <Typography variant="caption">
                Confidence: {(conditionsCheck.confidence * 100).toFixed(1)}%
              </Typography>
            )}
          </Alert>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Analytics />}
            onClick={() => {
              refetchAnalysis();
              refetchConditions();
            }}
            disabled={analysisLoading || conditionsLoading}
          >
            {analysisLoading || conditionsLoading ? <CircularProgress size={20} /> : 'Analyze'}
          </Button>

          <Button
            variant="contained"
            color="primary"
            startIcon={<PlayArrow />}
            onClick={() => setConfirmDialogOpen(true)}
            disabled={!conditionsCheck?.should_lend || executeMutation.isPending}
          >
            {executeMutation.isPending ? <CircularProgress size={20} /> : 'Execute Automated Lending'}
          </Button>
        </Box>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialogOpen} onClose={() => setConfirmDialogOpen(false)}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center' }}>
          <Warning sx={{ mr: 1, color: 'warning.main' }} />
          Confirm Automated Lending Execution
        </DialogTitle>

        <DialogContent>
          <Typography gutterBottom>
            You are about to execute automated lending with the following parameters:
          </Typography>

          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography><strong>Symbol:</strong> {selectedSymbol}</Typography>
            <Typography><strong>Amount:</strong> ${totalAmount} {useAllBalance ? '(All Available)' : ''}</Typography>
            <Typography><strong>Period:</strong> {period} days</Typography>
            <Typography><strong>Max Orders:</strong> {maxOrders}</Typography>
            {rateMin && <Typography><strong>Min Rate:</strong> {rateMin}%</Typography>}
            {rateMax && <Typography><strong>Max Rate:</strong> {rateMax}%</Typography>}
            {cancelExisting && <Typography color="error.main"><strong>Will cancel existing offers</strong></Typography>}
          </Box>

          <Alert severity="warning" sx={{ mt: 2 }}>
            This action will create lending offers on Bitfinex. Please ensure you understand the risks and have sufficient balance.
          </Alert>
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleExecute}
            variant="contained"
            color="primary"
            disabled={executeMutation.isPending}
          >
            {executeMutation.isPending ? <CircularProgress size={20} /> : 'Execute'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};