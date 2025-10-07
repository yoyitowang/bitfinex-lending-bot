import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  Paper,
  CircularProgress,
  Container,
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import type { LoginRequest } from '../types/api';

export const LoginForm: React.FC = () => {
  const { login } = useAuth();
  const [credentials, setCredentials] = useState<LoginRequest>({
    username: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(credentials);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof LoginRequest) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setCredentials(prev => ({
      ...prev,
      [field]: e.target.value,
    }));
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 8, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Bitfinex Lending API
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Sign In to Your Account
        </Typography>

        <Paper sx={{ p: 4, mt: 3 }}>
          <Box component="form" onSubmit={handleSubmit}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <TextField
              fullWidth
              label="Username"
              value={credentials.username}
              onChange={handleChange('username')}
              margin="normal"
              required
              disabled={isLoading}
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              value={credentials.password}
              onChange={handleChange('password')}
              margin="normal"
              required
              disabled={isLoading}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading || !credentials.username || !credentials.password}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
          </Box>

          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Demo credentials:
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', mt: 1 }}>
              username: testuser<br />
              password: password123
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};