import React, { useState, useEffect } from 'react';
import { bookingsAPI, paymentsAPI, reviewsAPI } from '../services/api';
import { toast } from 'react-toastify';
import './BookingsPage.css';

const BookingsPage = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewForm, setReviewForm] = useState({ bookingId: null, rating: 5, comment: '' });
  const [showReviewForm, setShowReviewForm] = useState(false);

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

  const handleCancel = async (bookingId) => {
    if (!window.confirm('Вы уверены, что хотите отменить бронирование?')) {
      return;
    }

    try {
      await bookingsAPI.cancel(bookingId);
      toast.success('Бронирование отменено');
      loadBookings();
    } catch (error) {
      toast.error('Ошибка отмены бронирования');
    }
  };

  const handlePay = async (bookingId) => {
    try {
      // Создаём платёж
      const paymentResponse = await paymentsAPI.create({
        booking: bookingId,
        payment_method: 'card'
      });

      // Обрабатываем платёж (имитация)
      await paymentsAPI.process(paymentResponse.data.id);
      
      toast.success('Оплата прошла успешно!');
      loadBookings();
    } catch (error) {
      toast.error('Ошибка оплаты');
    }
  };

  const openReviewForm = (bookingId) => {
    setReviewForm({ bookingId, rating: 5, comment: '' });
    setShowReviewForm(true);
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    
    const booking = bookings.find(b => b.id === reviewForm.bookingId);
    if (!booking) return;

    try {
      await reviewsAPI.create({
        booking: reviewForm.bookingId,  // Передаём ID бронирования вместо площадки
        rating: reviewForm.rating,
        comment: reviewForm.comment
      });
      
      toast.success('Отзыв отправлен на модерацию');
      setShowReviewForm(false);
      setReviewForm({ bookingId: null, rating: 5, comment: '' });
      loadBookings();  // Перезагружаем бронирования, чтобы обновить статус отзыва
    } catch (error) {
      const errorMsg = error.response?.data?.booking?.[0] || 
                       error.response?.data?.detail ||
                       'Ошибка создания отзыва';
      toast.error(errorMsg);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'status-confirmed';
      case 'pending': return 'status-pending';
      case 'cancelled': return 'status-cancelled';
      default: return '';
    }
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="bookings-page">
      <div className="container">
        <h1>Мои бронирования</h1>

        {bookings.length === 0 ? (
          <div className="no-bookings">
            <p>У вас пока нет бронирований</p>
          </div>
        ) : (
          <div className="bookings-list">
            {bookings.map(booking => (
              <div key={booking.id} className="booking-card">
                <div className="booking-header">
                  <h3>{booking.venue_details?.title}</h3>
                  <span className={`status-badge ${getStatusColor(booking.status)}`}>
                    {booking.status_display}
                  </span>
                </div>

                <div className="booking-details">
                  <div className="detail-row">
                    <span className="label">Адрес:</span>
                    <span>{booking.venue_details?.address}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Начало:</span>
                    <span>{new Date(booking.date_start).toLocaleString('ru-RU')}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Конец:</span>
                    <span>{new Date(booking.date_end).toLocaleString('ru-RU')}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Стоимость:</span>
                    <span className="price">{booking.total_price} ₽</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Дата создания:</span>
                    <span>{new Date(booking.created_at).toLocaleString('ru-RU')}</span>
                  </div>
                </div>

                <div className="booking-actions">
                  {booking.status === 'pending' && (
                    <>
                      <button 
                        className="btn btn-primary btn-sm"
                        onClick={() => handlePay(booking.id)}
                      >
                        Оплатить
                      </button>
                      <button 
                        className="btn btn-danger btn-sm"
                        onClick={() => handleCancel(booking.id)}
                      >
                        Отменить
                      </button>
                    </>
                  )}
                  
                  {booking.status === 'confirmed' && booking.can_be_cancelled && (
                    <button 
                      className="btn btn-danger btn-sm"
                      onClick={() => handleCancel(booking.id)}
                    >
                      Отменить
                    </button>
                  )}

                  {booking.status === 'confirmed' && 
                   new Date(booking.date_end) < new Date() && 
                   !booking.has_review && (
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => openReviewForm(booking.id)}
                    >
                      Оставить отзыв
                    </button>
                  )}
                  
                  {booking.has_review && (
                    <span className="review-status">✅ Отзыв оставлен</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {showReviewForm && (
          <div className="modal-overlay" onClick={() => setShowReviewForm(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>Оставить отзыв</h2>
              <form onSubmit={handleReviewSubmit}>
                <div className="form-group">
                  <label>Оценка</label>
                  <select
                    value={reviewForm.rating}
                    onChange={(e) => setReviewForm({...reviewForm, rating: Number(e.target.value)})}
                    required
                  >
                    <option value="5">⭐⭐⭐⭐⭐ (5)</option>
                    <option value="4">⭐⭐⭐⭐ (4)</option>
                    <option value="3">⭐⭐⭐ (3)</option>
                    <option value="2">⭐⭐ (2)</option>
                    <option value="1">⭐ (1)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Комментарий</label>
                  <textarea
                    value={reviewForm.comment}
                    onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                    rows="5"
                    required
                  />
                </div>

                <div className="modal-actions">
                  <button type="submit" className="btn btn-primary">
                    Отправить
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setShowReviewForm(false)}
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BookingsPage;

