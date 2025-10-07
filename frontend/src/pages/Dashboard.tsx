import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Card,
  CardContent,
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import { healthApi } from '../services/api';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  const { data: health, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.checkHealth,
    refetchInterval: 30000, // Check every 30 seconds
  });

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Dashboard
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3, mb: 3 }}>
          {/* Welcome Card */}
          <Box sx={{ flex: 1 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Welcome back, {user?.username || 'User'}!
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  User ID: {user?.user_id}
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* API Health Card */}
          <Box sx={{ flex: 1 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  API Health Status
                </Typography>
                {isLoading ? (
                  <Typography>Loading...</Typography>
                ) : (
                  <Box>
                    <Typography>Status: <strong>{health?.status}</strong></Typography>
                    <Typography>Service: <strong>{health?.service}</strong></Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Features Overview */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Available Features
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, flexWrap: 'wrap' }}>
            <Card sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' }, p: 2 }}>
              <Typography variant="subtitle1">📊 Market Data</Typography>
              <Typography variant="body2" color="text.secondary">
                Real-time cryptocurrency market data
              </Typography>
            </Card>
            <Card sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' }, p: 2 }}>
              <Typography variant="subtitle1">💰 Lending Orders</Typography>
              <Typography variant="body2" color="text.secondary">
                Create and manage lending positions
              </Typography>
            </Card>
            <Card sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' }, p: 2 }}>
              <Typography variant="subtitle1">📈 Portfolio</Typography>
              <Typography variant="body2" color="text.secondary">
                Track your lending portfolio performance
              </Typography>
            </Card>
            <Card sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' }, p: 2 }}>
              <Typography variant="subtitle1">🤖 Automation</Typography>
              <Typography variant="body2" color="text.secondary">
                Automated lending strategies
              </Typography>
            </Card>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};