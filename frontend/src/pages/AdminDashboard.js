import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { venuesAPI, bookingsAPI, reviewsAPI, authAPI } from '../services/api';
import { toast } from 'react-toastify';
import './AdminDashboard.css';

const AdminDashboard = () => {
  return (
    <div className="admin-dashboard">
      <div className="admin-sidebar">
        <h2>Админ-панель</h2>
        <nav className="admin-nav">
          <Link to="/admin" className="admin-nav-link">Обзор</Link>
          <Link to="/admin/venues" className="admin-nav-link">Площадки</Link>
          <Link to="/admin/bookings" className="admin-nav-link">Бронирования</Link>
          <Link to="/admin/reviews" className="admin-nav-link">Отзывы</Link>
          <Link to="/admin/users" className="admin-nav-link">Пользователи</Link>
        </nav>
      </div>

      <div className="admin-content">
        <Routes>
          <Route path="/" element={<AdminOverview />} />
          <Route path="/venues" element={<AdminVenues />} />
          <Route path="/bookings" element={<AdminBookings />} />
          <Route path="/reviews" element={<AdminReviews />} />
          <Route path="/users" element={<AdminUsers />} />
        </Routes>
      </div>
    </div>
  );
};

const AdminOverview = () => {
  const [stats, setStats] = useState({
    venues: 0,
    bookings: 0,
    reviews: 0,
    users: 0
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [venuesRes, bookingsRes, reviewsRes, usersRes] = await Promise.all([
        venuesAPI.getAll(),
        bookingsAPI.getAll(),
        reviewsAPI.getPending(),
        authAPI.getProfile() // Для примера
      ]);

      setStats({
        venues: venuesRes.data.count || venuesRes.data.length || 0,
        bookings: bookingsRes.data.count || bookingsRes.data.length || 0,
        reviews: reviewsRes.data.count || reviewsRes.data.length || 0,
        users: 1 // Placeholder
      });
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  return (
    <div className="admin-overview">
      <h1>Обзор системы</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🏢</div>
          <div className="stat-value">{stats.venues}</div>
          <div className="stat-label">Площадок</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-value">{stats.bookings}</div>
          <div className="stat-label">Бронирований</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-value">{stats.reviews}</div>
          <div className="stat-label">На модерации</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-value">{stats.users}</div>
          <div className="stat-label">Активных</div>
        </div>
      </div>
    </div>
  );
};

const AdminVenues = () => {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVenues();
  }, []);

  const loadVenues = async () => {
    try {
      const response = await venuesAPI.getAll();
      setVenues(response.data.results || response.data);
    } catch (error) {
      toast.error('Ошибка загрузки площадок');
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (id, isActive) => {
    try {
      await venuesAPI.update(id, { is_active: !isActive });
      toast.success('Статус изменён');
      loadVenues();
    } catch (error) {
      toast.error('Ошибка изменения статуса');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="admin-section">
      <h1>Управление площадками</h1>
      <div className="admin-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Адрес</th>
              <th>Цена/час</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {venues.map(venue => (
              <tr key={venue.id}>
                <td>{venue.id}</td>
                <td>{venue.title}</td>
                <td>{venue.address}</td>
                <td>{venue.price_per_hour} ₽</td>
                <td>
                  <span className={`badge ${venue.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {venue.is_active ? 'Активна' : 'Неактивна'}
                  </span>
                </td>
                <td>
                  <button 
                    className="btn btn-sm btn-secondary"
                    onClick={() => toggleActive(venue.id, venue.is_active)}
                  >
                    {venue.is_active ? 'Деактивировать' : 'Активировать'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const AdminBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    try {
      const response = await bookingsAPI.getAll();
      setBookings(response.data.results || response.data);
    } catch (error) {
      toast.error('Ошибка загрузки бронирований');
    } finally {
      setLoading(false);
    }
  };

  const confirmBooking = async (id) => {
    try {
      await bookingsAPI.confirm(id);
      toast.success('Бронирование подтверждено');
      loadBookings();
    } catch (error) {
      toast.error('Ошибка подтверждения');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="admin-section">
      <h1>Управление бронированиями</h1>
      <div className="admin-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Пользователь</th>
              <th>Площадка</th>
              <th>Дата</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {bookings.map(booking => (
              <tr key={booking.id}>
                <td>{booking.id}</td>
                <td>{booking.user_name}</td>
                <td>{booking.venue_details?.title}</td>
                <td>{new Date(booking.date_start).toLocaleDateString('ru-RU')}</td>
                <td>
                  <span className={`badge badge-${booking.status}`}>
                    {booking.status_display}
                  </span>
                </td>
                <td>
                  {booking.status === 'pending' && (
                    <button 
                      className="btn btn-sm btn-primary"
                      onClick={() => confirmBooking(booking.id)}
                    >
                      Подтвердить
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const AdminReviews = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReviews();
  }, []);

  const loadReviews = async () => {
    try {
      const response = await reviewsAPI.getPending();
      setReviews(response.data.results || response.data);
    } catch (error) {
      toast.error('Ошибка загрузки отзывов');
    } finally {
      setLoading(false);
    }
  };

  const approveReview = async (id) => {
    try {
      await reviewsAPI.approve(id);
      toast.success('Отзыв одобрен');
      loadReviews();
    } catch (error) {
      toast.error('Ошибка одобрения отзыва');
    }
  };

  const disapproveReview = async (id) => {
    try {
      await reviewsAPI.disapprove(id);
      toast.success('Отзыв отклонён');
      loadReviews();
    } catch (error) {
      toast.error('Ошибка отклонения отзыва');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="admin-section">
      <h1>Модерация отзывов</h1>
      {reviews.length === 0 ? (
        <p className="no-data">Нет отзывов на модерации</p>
      ) : (
        <div className="reviews-admin-list">
          {reviews.map(review => (
            <div key={review.id} className="review-admin-card">
              <div className="review-admin-header">
                <strong>{review.user_name || review.user_username}</strong>
                <span>⭐ {review.rating}/5</span>
              </div>
              <p className="review-venue">{review.venue_title}</p>
              <p className="review-text">{review.comment}</p>
              <div className="review-actions">
                <button 
                  className="btn btn-sm btn-primary"
                  onClick={() => approveReview(review.id)}
                >
                  Одобрить
                </button>
                <button 
                  className="btn btn-sm btn-danger"
                  onClick={() => disapproveReview(review.id)}
                >
                  Отклонить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const AdminUsers = () => {
  return (
    <div className="admin-section">
      <h1>Управление пользователями</h1>
      <p>Для управления пользователями используйте стандартную админ-панель Django по адресу: <a href="http://localhost:8000/admin" target="_blank" rel="noopener noreferrer">http://localhost:8000/admin</a></p>
    </div>
  );
};

export default AdminDashboard;

