import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Auth Pages
import LoginPage from './pages/LoginPage';

// Student Pages
import DashboardPage from './pages/DashboardPage';
import ExamsListPage from './pages/ExamsListPage';
import ExamSessionPage from './pages/ExamSessionPage';
import MyResultsPage from './pages/MyResultsPage';

// Admin Pages
import AdminDashboardPage from './pages/admin/AdminDashboardPage';
import ExamManagementPage from './pages/admin/ExamManagementPage';
import CreateExamPage from './pages/admin/CreateExamPage';
import EditExamPage from './pages/admin/EditExamPage';
import SuspiciousAttemptsPage from './pages/admin/SuspiciousAttemptsPage';
import BlockchainAuditPage from './pages/admin/BlockchainAuditPage';
import StudentManagementPage from './pages/admin/StudentManagementPage';

import './App.css';

// Root redirect component
const RootRedirect = () => {
  const { user } = useAuth();

  if (user?.role === 'admin') {
    return <Navigate to="/admin" replace />;
  }
  return <Navigate to="/dashboard" replace />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Root - Redirect based on role */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <RootRedirect />
              </ProtectedRoute>
            }
          />

          {/* Student Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requireAdmin={false}>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/exams"
            element={
              <ProtectedRoute requireAdmin={false}>
                <ExamsListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/exam/:examId"
            element={
              <ProtectedRoute requireAdmin={false}>
                <ExamSessionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-results"
            element={
              <ProtectedRoute requireAdmin={false}>
                <MyResultsPage />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
          {/* Exam routes - specific before general */}
          <Route
            path="/admin/exams/new"
            element={
              <ProtectedRoute requireAdmin={true}>
                <CreateExamPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/exams/:id/edit"
            element={
              <ProtectedRoute requireAdmin={true}>
                <EditExamPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/exams"
            element={
              <ProtectedRoute requireAdmin={true}>
                <ExamManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/suspicious"
            element={
              <ProtectedRoute requireAdmin={true}>
                <SuspiciousAttemptsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/blockchain"
            element={
              <ProtectedRoute requireAdmin={true}>
                <BlockchainAuditPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/students"
            element={
              <ProtectedRoute requireAdmin={true}>
                <StudentManagementPage />
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to root */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
