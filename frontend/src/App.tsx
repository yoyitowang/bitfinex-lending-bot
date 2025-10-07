import { Routes, Route, Navigate } from 'react-router-dom'
import { Container, Typography, Box } from '@mui/material'
import { useAuth } from './hooks/useAuth'
import { LoginForm } from './components/LoginForm'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { MarketData } from './pages/MarketData'
import { Lending } from './pages/Lending'
import { Portfolio } from './pages/Portfolio'
import { Settings } from './pages/Settings'

function LoginPage() {
  return <LoginForm />;
}

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ my: 8, textAlign: 'center' }}>
          <Typography variant="h6">Loading...</Typography>
        </Box>
      </Container>
    )
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/market-data" element={<MarketData />} />
        <Route path="/lending" element={<Lending />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
