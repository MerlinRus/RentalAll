import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <img src="/logo.png" alt="RentalAll" className="navbar-logo-img" />
          <span className="navbar-logo-text">RentalAll</span>
        </Link>

        <div className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <Link to="/" className="navbar-link" onClick={() => setMobileMenuOpen(false)}>
            Главная
          </Link>
          <Link to="/venues" className="navbar-link" onClick={() => setMobileMenuOpen(false)}>
            Площадки
          </Link>
          <Link to="/map" className="navbar-link" onClick={() => setMobileMenuOpen(false)}>
            Карта
          </Link>

          {user ? (
            <>
              <Link to="/bookings" className="navbar-link" onClick={() => setMobileMenuOpen(false)}>
                Мои бронирования
              </Link>
              <Link to="/profile" className="navbar-link" onClick={() => setMobileMenuOpen(false)}>
                Профиль
              </Link>
              {isAdmin() && (
                <Link to="/admin" className="navbar-link admin-link" onClick={() => setMobileMenuOpen(false)}>
                  Админ-панель
                </Link>
              )}
              <button onClick={handleLogout} className="navbar-link navbar-button">
                Выход
              </button>
              <span className="navbar-user">
                {user.full_name || user.username}
              </span>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link" onClick={() => setMobileMenuOpen(false)}>
                Вход
              </Link>
              <Link to="/register" className="navbar-link navbar-register" onClick={() => setMobileMenuOpen(false)}>
                Регистрация
              </Link>
            </>
          )}
        </div>

        <button className="navbar-toggle" onClick={toggleMobileMenu}>
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;

