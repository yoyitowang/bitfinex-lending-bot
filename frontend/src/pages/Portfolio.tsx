import React from 'react';
import {
  Container,
  Typography,
  Box,
} from '@mui/material';
import { PortfolioOverview } from '../components/PortfolioOverview';

export const Portfolio: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Portfolio Overview
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Monitor your lending positions, earnings, and portfolio performance
        </Typography>

        <PortfolioOverview />
      </Box>
    </Container>
  );
};