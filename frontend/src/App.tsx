import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Components
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import InterviewSession from './pages/interview/InterviewSession';
import InterviewHistory from './pages/interview/InterviewHistory';
import InterviewAnalysis from './pages/interview/InterviewAnalysis';
import CodingAssessment from './pages/assessment/CodingAssessment';
import MCQAssessment from './pages/assessment/MCQAssessment';
import AssessmentHistory from './pages/assessment/AssessmentHistory';

// Context
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <WebSocketProvider>
            <Router>
              <Box sx={{ display: 'flex', minHeight: '100vh' }}>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  
                  {/* Protected Routes */}
                  <Route path="/*" element={
                    <ProtectedRoute>
                      <Box sx={{ display: 'flex', width: '100%' }}>
                        <Sidebar />
                        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                          <Navbar />
                          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
                            <Routes>
                              <Route path="/" element={<Navigate to="/dashboard" replace />} />
                              <Route path="/dashboard" element={<Dashboard />} />
                              <Route path="/profile" element={<Profile />} />
                              
                              {/* Interview Routes */}
                              <Route path="/interview/session/:sessionId" element={<InterviewSession />} />
                              <Route path="/interview/history" element={<InterviewHistory />} />
                              <Route path="/interview/analysis/:sessionId" element={<InterviewAnalysis />} />
                              
                              {/* Assessment Routes */}
                              <Route path="/assessment/coding/:assessmentId" element={<CodingAssessment />} />
                              <Route path="/assessment/mcq/:assessmentId" element={<MCQAssessment />} />
                              <Route path="/assessment/history" element={<AssessmentHistory />} />
                              
                              {/* Fallback */}
                              <Route path="*" element={<Navigate to="/dashboard" replace />} />
                            </Routes>
                          </Box>
                        </Box>
                      </Box>
                    </ProtectedRoute>
                  } />
                </Routes>
              </Box>
              
              {/* Toast notifications */}
              <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="light"
              />
            </Router>
          </WebSocketProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
