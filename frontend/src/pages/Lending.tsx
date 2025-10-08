import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Alert,
  Snackbar,
  Tab,
  Tabs,
} from '@mui/material';
import { Add as AddIcon, AutoAwesome as AutoIcon } from '@mui/icons-material';
import { LendingOrderForm } from '../components/LendingOrderForm';
import { AutomatedLendingControls } from '../components/AutomatedLendingControls';

export const Lending: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'manual' | 'automated'>('manual');
  const [showForm, setShowForm] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');

  const handleCreateOffer = () => {
    setShowForm(true);
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setSuccessMessage('Lending offer created successfully!');
  };

  const handleCancelForm = () => {
    setShowForm(false);
  };

  const handleCloseSnackbar = () => {
    setSuccessMessage('');
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: 'manual' | 'automated') => {
    setActiveTab(newValue);
    setShowForm(false);
  };

  const handleAutomatedExecute = () => {
    setSuccessMessage('Automated lending executed successfully!');
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Lending Management
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Create and manage your cryptocurrency lending offers
          </Typography>

          <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab
              value="manual"
              label="Manual Orders"
              icon={<AddIcon />}
              iconPosition="start"
            />
            <Tab
              value="automated"
              label="Automated Lending"
              icon={<AutoIcon />}
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {activeTab === 'manual' && (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
              {!showForm && (
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<AddIcon />}
                  onClick={handleCreateOffer}
                  sx={{ minWidth: 200 }}
                >
                  Create Lending Offer
                </Button>
              )}
            </Box>

            {showForm ? (
              <LendingOrderForm
                onSuccess={handleFormSuccess}
                onCancel={handleCancelForm}
              />
            ) : (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Active Lending Offers
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                  Start earning interest by lending your cryptocurrencies to borrowers on the platform.
                </Typography>

                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3, maxWidth: 800, mx: 'auto' }}>
                  <Box sx={{ p: 3, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                    <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
                      💰 Earn Interest
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Lend your crypto assets and earn competitive interest rates from borrowers.
                    </Typography>
                  </Box>

                  <Box sx={{ p: 3, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                    <Typography variant="h6" gutterBottom sx={{ color: 'success.main' }}>
                      🔒 Secure Platform
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Your assets remain secure with our audited smart contracts and escrow system.
                    </Typography>
                  </Box>

                  <Box sx={{ p: 3, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                    <Typography variant="h6" gutterBottom sx={{ color: 'warning.main' }}>
                      📊 Flexible Terms
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Set your own lending terms including rates, amounts, and duration periods.
                    </Typography>
                  </Box>
                </Box>
              </Box>
            )}
          </>
        )}

        {activeTab === 'automated' && (
          <AutomatedLendingControls onExecute={handleAutomatedExecute} />
        )}
      </Box>

      {/* Success Snackbar */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          {successMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};