import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import Login from './components/auth/Login';
import SignUp from './components/auth/SignUp';
import Dashboard from './components/dashboard/Dashboard';
import Assessment from './components/assessment/Assessment';
import SkillsSelection from './components/skills/SkillsSelection';
import CareerPath from './components/career/CareerPath';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';

function AppRoutes() {
  const { isAuthenticated } = useAuth();
  
  return (
    <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
        <Route path="/signup" element={!isAuthenticated ? <SignUp /> : <Navigate to="/dashboard" />} />
        
        <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/assessment" element={<Assessment />} />
            <Route path="/skills" element={<SkillsSelection />} />
            <Route path="/career" element={<CareerPath />} />
        </Route>
        </Route>
        
        <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
            <AppRoutes />
        </BrowserRouter>
    </AuthProvider>    
  );
}

export default App;