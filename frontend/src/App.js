import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';
import PrivateRoute from './components/Auth/PrivateRoute';
import AdminRoute from './components/Auth/AdminRoute';

// Pages
import HomePage from './pages/HomePage';
import VenueListPage from './pages/VenueListPage';
import VenueDetailPage from './pages/VenueDetailPage';
import MapPage from './pages/MapPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import BookingsPage from './pages/BookingsPage';
import AdminDashboard from './pages/AdminDashboard';
import NotFoundPage from './pages/NotFoundPage';

import './App.css';

// Компонент для условного рендеринга Footer
function ConditionalFooter() {
  const location = useLocation();
  // Не показываем Footer на странице карты
  if (location.pathname === '/map') {
    return null;
  }
  return <Footer />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <Routes>
              {/* Публичные маршруты */}
              <Route path="/" element={<HomePage />} />
              <Route path="/venues" element={<VenueListPage />} />
              <Route path="/venues/:id" element={<VenueDetailPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Защищенные маршруты */}
              <Route path="/profile" element={
                <PrivateRoute>
                  <ProfilePage />
                </PrivateRoute>
              } />
              <Route path="/bookings" element={
                <PrivateRoute>
                  <BookingsPage />
                </PrivateRoute>
              } />
              
              {/* Админские маршруты */}
              <Route path="/admin/*" element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              } />
              
              {/* 404 */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
          <ConditionalFooter />
          <ToastContainer position="bottom-right" autoClose={3000} />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

