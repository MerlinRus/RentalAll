import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminRoute = ({ children }) => {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return (
      <div className="loading">
        Загрузка...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return isAdmin() ? children : <Navigate to="/" />;
};

export default AdminRoute;

