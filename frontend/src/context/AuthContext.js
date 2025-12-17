import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Проверка токена и загрузка пользователя при монтировании
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      try {
        // Проверка срока действия токена
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        
        if (decoded.exp < currentTime) {
          // Токен истек, пытаемся обновить
          await refreshToken();
        } else {
          // Токен валиден, загружаем профиль
          await loadUser();
        }
      } catch (error) {
        console.error('Ошибка проверки аутентификации:', error);
        logout();
      }
    }
    
    setLoading(false);
  };

  const loadUser = async () => {
    try {
      const response = await authAPI.getProfile();
      setUser(response.data);
    } catch (error) {
      console.error('Ошибка загрузки пользователя:', error);
      logout();
    }
  };

  const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    
    if (!refresh) {
      logout();
      return;
    }

    try {
      const response = await authAPI.login(); // Используем интерцептор для обновления
      const { access } = response.data;
      localStorage.setItem('access_token', access);
      await loadUser();
    } catch (error) {
      logout();
    }
  };

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      await loadUser();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Ошибка входа',
      };
    }
  };

  const register = async (userData) => {
    try {
      await authAPI.register(userData);
      // После регистрации автоматически входим
      return await login(userData.username, userData.password);
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || 'Ошибка регистрации',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const isAdmin = () => {
    return user && (user.role === 'admin' || user.is_staff);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin,
    refreshUser: loadUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

