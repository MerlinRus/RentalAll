import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { venuesAPI, reviewsAPI, bookingsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import ImageGallerySlider from '../components/ImageGallerySlider';
import './VenueDetailPage.css';

const VenueDetailPage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [venue, setVenue] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bookingMode, setBookingMode] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);
  const [occupiedSlots, setOccupiedSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    loadVenue();
    loadReviews();
  }, [id]);

  const loadVenue = async () => {
    try {
      const response = await venuesAPI.getById(id);
      setVenue(response.data);
    } catch (error) {
      toast.error('Ошибка загрузки площадки');
      navigate('/venues');
    } finally {
      setLoading(false);
    }
  };

  const loadReviews = async () => {
    try {
      const response = await reviewsAPI.getAll({ venue: id });
      setReviews(response.data.results || response.data);
    } catch (error) {
      console.error('Ошибка загрузки отзывов:', error);
    }
  };

  // Генерация временных слотов (каждые 30 минут с 8:00 до 23:00)
  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 8; hour < 23; hour++) {
      slots.push(`${hour.toString().padStart(2, '0')}:00`);
      slots.push(`${hour.toString().padStart(2, '0')}:30`);
    }
    slots.push('23:00');
    return slots;
  };

  // Загрузка занятых слотов для выбранной даты
  const loadOccupiedSlots = async (date) => {
    if (!venue) return;
    
    setLoadingSlots(true);
    try {
      // Используем локальные методы даты для правильного форматирования
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const dateStr = `${year}-${month}-${day}`;
      
      const response = await bookingsAPI.getOccupiedSlots(venue.id, dateStr);
      setOccupiedSlots(response.data.occupied_slots || []);
    } catch (error) {
      console.error('Ошибка загрузки занятых слотов:', error);
      setOccupiedSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  // Проверка, занят ли слот (или находится в занятом диапазоне)
  const isSlotOccupied = (timeSlot) => {
    const result = occupiedSlots.some(occupied => {
      const [occStart, occEnd] = occupied.split(' - ');
      // Слот считается занятым, если он >= начала И < конца бронирования
      return timeSlot >= occStart && timeSlot < occEnd;
    });
    return result;
  };

  // Проверка, находится ли слот в прошлом
  const isSlotInPast = (timeSlot) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const selectedDay = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate());
    
    // Если выбранная дата не сегодня, слот не в прошлом
    if (selectedDay.getTime() !== today.getTime()) {
      return false;
    }
    
    // Если дата = сегодня, сравниваем время
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${Math.floor(now.getMinutes() / 30) * 30}`;
    return timeSlot < currentTime;
  };

  // Проверка, можно ли выбрать слот как конечный
  const isValidEndTime = (time) => {
    if (!startTime) return false;
    if (time <= startTime) return false;
    
    // Проверяем, что между началом и концом нет занятых слотов
    const allSlots = generateTimeSlots();
    const startIndex = allSlots.indexOf(startTime);
    const endIndex = allSlots.indexOf(time);
    
    for (let i = startIndex; i < endIndex; i++) {
      if (isSlotOccupied(allSlots[i])) {
        return false;
      }
    }
    return true;
  };

  // Загрузка занятых слотов при смене даты или включении режима бронирования
  useEffect(() => {
    if (bookingMode && venue) {
      loadOccupiedSlots(selectedDate);
      setStartTime(null);
      setEndTime(null);
    }
  }, [selectedDate, bookingMode]);

  const calculatePrice = () => {
    if (!startTime || !endTime) return 0;
    
    const allSlots = generateTimeSlots();
    const startIndex = allSlots.indexOf(startTime);
    const endIndex = allSlots.indexOf(endTime);
    const halfHours = endIndex - startIndex;
    const hours = halfHours * 0.5;
    
    return (hours * parseFloat(venue?.price_per_hour || 0)).toFixed(2);
  };

  const handleBooking = async () => {
    if (!user) {
      toast.info('Войдите, чтобы забронировать площадку');
      navigate('/login');
      return;
    }

    if (!startTime || !endTime) {
      toast.error('Выберите время начала и конца бронирования');
      return;
    }

    try {
      // Создаем даты используя конструктор Date с параметрами (гарантированно local time)
      const [startHour, startMinute] = startTime.split(':').map(Number);
      const [endHour, endMinute] = endTime.split(':').map(Number);
      
      const startDateTime = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        selectedDate.getDate(),
        startHour,
        startMinute,
        0
      );
      
      const endDateTime = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        selectedDate.getDate(),
        endHour,
        endMinute,
        0
      );

      console.log('Sending booking:', {
        start_local: startDateTime.toString(),
        start_iso: startDateTime.toISOString(),
        end_local: endDateTime.toString(),
        end_iso: endDateTime.toISOString()
      });

      await bookingsAPI.create({
        venue: venue.id,
        date_start: startDateTime.toISOString(),
        date_end: endDateTime.toISOString()
      });
      toast.success('Бронирование создано!');
      navigate('/bookings');
    } catch (error) {
      console.error('Ошибка бронирования:', error.response?.data);
      
      // Получаем детальное сообщение об ошибке
      let errorMsg = 'Ошибка создания бронирования';
      
      if (error.response?.data) {
        const data = error.response.data;
        if (typeof data === 'string') {
          errorMsg = data;
        } else if (data.venue) {
          errorMsg = Array.isArray(data.venue) ? data.venue[0] : data.venue;
        } else if (data.date_start) {
          errorMsg = Array.isArray(data.date_start) ? data.date_start[0] : data.date_start;
        } else if (data.date_end) {
          errorMsg = Array.isArray(data.date_end) ? data.date_end[0] : data.date_end;
        } else if (data.detail) {
          errorMsg = data.detail;
        } else if (data.non_field_errors) {
          errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors;
        }
      }
      
      toast.error(errorMsg);
    }
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (!venue) {
    return <div className="error">Площадка не найдена</div>;
  }

  return (
    <div className="venue-detail-page">
      <div className="container">
        <ImageGallerySlider images={venue.images} venueName={venue.title} />

        <div className="venue-main-info">
          <div className="venue-header">
            <h1>{venue.title}</h1>
            {venue.average_rating > 0 && (
              <div className="rating">
                ⭐ {venue.average_rating} ({venue.reviews_count} отзывов)
              </div>
            )}
          </div>

          <div className="venue-details">
            <div className="detail-item">
              <strong>Вместимость:</strong> {venue.capacity} человек
            </div>
            <div className="detail-item">
              <strong>Цена:</strong> {venue.price_per_hour} ₽/час
            </div>
            <div className="detail-item">
              <strong>Адрес:</strong> {venue.address}
            </div>
            {venue.categories && venue.categories.length > 0 && (
              <div className="detail-item">
                <strong>Категории:</strong>
                <div className="categories">
                  {venue.categories.map(cat => (
                    <span key={cat.id} className="category-tag">{cat.name}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="venue-description">
            <h2>Описание</h2>
            <p>{venue.description}</p>
          </div>

          {/* Кнопка "Посмотреть на карте" */}
          {venue.latitude && venue.longitude && (
            <div className="map-link-section">
              <button 
                className="btn-map-link" 
                onClick={() => navigate(`/map?venue=${venue.id}`)}
              >
                🗺️ Посмотреть на карте
              </button>
            </div>
          )}

          <div className="booking-section">
            <h2>Бронирование</h2>
            {!bookingMode ? (
              <button 
                className="btn btn-primary btn-large" 
                onClick={() => setBookingMode(true)}
              >
                Забронировать площадку
              </button>
            ) : (
              <div className="booking-form">
                <div className="date-picker-group">
                  <label>Выберите дату</label>
                  <DatePicker
                    selected={selectedDate}
                    onChange={setSelectedDate}
                    dateFormat="dd.MM.yyyy"
                    minDate={new Date()}
                    inline
                  />
                </div>

                {loadingSlots ? (
                  <div className="loading-slots">Загрузка доступных слотов...</div>
                ) : (
                  <>
                    <div className="time-selection">
                      <h3>Выберите время начала</h3>
                      <div className="time-slots">
                        {(() => {
                          const allSlots = generateTimeSlots();
                          
                          return allSlots.map(slot => {
                            const occupied = isSlotOccupied(slot);
                            const inPast = isSlotInPast(slot);
                            const selected = startTime === slot;
                            
                            if (occupied || inPast) return null; // Не показываем занятые и прошедшие слоты
                            
                            return (
                              <button
                                key={slot}
                                className={`time-slot ${selected ? 'selected' : ''}`}
                                onClick={() => {
                                  setStartTime(slot);
                                  setEndTime(null); // Сбрасываем конечное время
                                }}
                              >
                                {slot}
                              </button>
                            );
                          });
                        })()}
                      </div>
                    </div>

                    {startTime && (
                      <div className="time-selection">
                        <h3>Выберите время окончания</h3>
                        <div className="time-slots">
                          {generateTimeSlots().map(slot => {
                            const validEnd = isValidEndTime(slot);
                            const selected = endTime === slot;
                            
                            if (!validEnd) return null; // Не показываем недоступные слоты
                            
                            return (
                              <button
                                key={slot}
                                className={`time-slot ${selected ? 'selected' : ''}`}
                                onClick={() => setEndTime(slot)}
                              >
                                {slot}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {startTime && endTime && (
                      <div className="booking-summary">
                        <div className="booking-info">
                          <p><strong>Дата:</strong> {selectedDate.toLocaleDateString('ru-RU')}</p>
                          <p><strong>Время:</strong> {startTime} - {endTime}</p>
                          <p className="booking-price">
                            <strong>Общая стоимость:</strong> {calculatePrice()} ₽
                          </p>
                        </div>
                      </div>
                    )}
                  </>
                )}

                <div className="booking-actions">
                  <button 
                    className="btn btn-primary" 
                    onClick={handleBooking}
                    disabled={!startTime || !endTime || loadingSlots}
                  >
                    Подтвердить бронирование
                  </button>
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => {
                      setBookingMode(false);
                      setStartTime(null);
                      setEndTime(null);
                    }}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="reviews-section">
          <h2>Отзывы</h2>
          {reviews.length === 0 ? (
            <p className="no-reviews">Пока нет отзывов</p>
          ) : (
            <div className="reviews-list">
              {reviews.map(review => (
                <div key={review.id} className="review-card">
                  <div className="review-header">
                    <strong>{review.user_name || review.user_username}</strong>
                    <span className="review-rating">⭐ {review.rating}/5</span>
                  </div>
                  <p className="review-comment">{review.comment}</p>
                  <span className="review-date">
                    {new Date(review.created_at).toLocaleDateString('ru-RU')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VenueDetailPage;

