import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './HomePage.css';

const HomePage = () => {
  const { user } = useAuth();

  return (
    <div className="home-page">
      <section className="hero">
        <div className="hero-content">
          <img src="/logo.png" alt="RentalAll" className="hero-logo" />
          <h1>Добро пожаловать в RentalAll</h1>
          <p>Найдите идеальную площадку для вашего мероприятия</p>
          <Link to="/venues" className="btn btn-primary btn-large">
            Посмотреть площадки
          </Link>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2>Преимущества платформы</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🏢</div>
              <h3>Широкий выбор</h3>
              <p>Множество площадок различного типа и вместимости</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">💳</div>
              <h3>Онлайн бронирование</h3>
              <p>Забронируйте площадку за несколько кликов</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⭐</div>
              <h3>Отзывы пользователей</h3>
              <p>Читайте отзывы и делитесь своим опытом</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Безопасные платежи</h3>
              <p>Защищенная система оплаты бронирований</p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="container">
          <h2>Как это работает</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Выберите площадку</h3>
              <p>Просмотрите каталог и найдите подходящую площадку</p>
            </div>
            
            <div className="step">
              <div className="step-number">2</div>
              <h3>Забронируйте</h3>
              <p>Выберите дату и время, создайте бронирование</p>
            </div>
            
            <div className="step">
              <div className="step-number">3</div>
              <h3>Оплатите</h3>
              <p>Произведите оплату онлайн</p>
            </div>
            
            <div className="step">
              <div className="step-number">4</div>
              <h3>Проведите мероприятие</h3>
              <p>Наслаждайтесь своим мероприятием</p>
            </div>
          </div>
        </div>
      </section>

      {!user && (
        <section className="cta">
          <div className="container">
            <h2>Готовы начать?</h2>
            <p>Зарегистрируйтесь и забронируйте свою первую площадку</p>
            <Link to="/register" className="btn btn-primary btn-large">
              Зарегистрироваться
            </Link>
          </div>
        </section>
      )}
    </div>
  );
};

export default HomePage;

