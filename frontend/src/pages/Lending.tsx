import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
} from '@mui/material';

export const Lending: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Lending Orders
        </Typography>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Coming Soon
          </Typography>
          <Typography>
            Lending order management interface will be displayed here.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};