import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { venuesAPI, categoriesAPI } from '../services/api';
import { toast } from 'react-toastify';
import './MapPage.css';

const MapPage = () => {
  const [venues, setVenues] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const targetVenueId = searchParams.get('venue');
  const mapRef = useRef(null);
  const ymapsRef = useRef(null);
  const placemarkRefs = useRef({});
  
  // Состояния для bottom sheet (мобильная версия)
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [bottomSheetOpen, setBottomSheetOpen] = useState(false);
  const [bottomSheetExpanded, setBottomSheetExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const bottomSheetRef = useRef(null);
  const startYRef = useRef(0);
  const currentTranslateRef = useRef(0);

  // Отслеживание изменения размера экрана
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) {
        setBottomSheetOpen(false);
        setBottomSheetExpanded(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Обработка открытия площадки в bottom sheet
  const handleVenueClick = (venue) => {
    if (isMobile) {
      setSelectedVenue(venue);
      setBottomSheetOpen(true);
      setBottomSheetExpanded(false);
    }
  };

  // Touch handlers для drag bottom sheet
  const handleTouchStart = (e) => {
    startYRef.current = e.touches[0].clientY;
    currentTranslateRef.current = bottomSheetExpanded ? 0 : 60;
  };

  const handleTouchMove = (e) => {
    if (!bottomSheetRef.current) return;
    
    const currentY = e.touches[0].clientY;
    const diff = startYRef.current - currentY;
    const newTranslate = currentTranslateRef.current - diff;
    
    // Ограничиваем движение
    if (newTranslate >= 0 && newTranslate <= 100) {
      bottomSheetRef.current.style.transform = `translateY(${newTranslate}%)`;
    }
  };

  const handleTouchEnd = (e) => {
    if (!bottomSheetRef.current) return;
    
    const endY = e.changedTouches[0].clientY;
    const diff = startYRef.current - endY;
    
    // Если свайпнули вверх больше чем на 50px - раскрываем
    if (diff > 50 && !bottomSheetExpanded) {
      setBottomSheetExpanded(true);
    }
    // Если свайпнули вниз больше чем на 50px - сворачиваем или закрываем
    else if (diff < -50) {
      if (bottomSheetExpanded) {
        setBottomSheetExpanded(false);
      } else {
        setBottomSheetOpen(false);
      }
    }
    
    // Возвращаем в исходное положение
    bottomSheetRef.current.style.transform = '';
  };

  // Загрузка категорий
  const loadCategories = async () => {
    try {
      const response = await categoriesAPI.getAll();
      const data = Array.isArray(response.data) ? response.data : response.data.results || [];
      setCategories(data);
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
    }
  };

  // Загрузка площадок
  const loadVenues = useCallback(async () => {
    try {
      const params = selectedCategories.length > 0 
        ? { category: selectedCategories.join(',') } 
        : {};
      
      const response = await venuesAPI.getAll(params);
      const data = Array.isArray(response.data) ? response.data : response.data.results || [];
      setVenues(data);
    } catch (error) {
      toast.error('Ошибка загрузки площадок');
      console.error('Ошибка загрузки площадок:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedCategories]);

  // Инициализация карты
  const initMap = useCallback(() => {
    if (!window.ymaps || !mapRef.current) {
      return;
    }

    try {
      window.ymaps.ready(() => {
        try {
          if (ymapsRef.current) {
            ymapsRef.current.destroy();
          }

          const venuesWithCoords = venues.filter(v => v.latitude && v.longitude);
          
          let center, zoom;
          
          const targetVenue = targetVenueId ? venuesWithCoords.find(v => v.id === parseInt(targetVenueId)) : null;
          
          if (targetVenue) {
            center = [parseFloat(targetVenue.latitude), parseFloat(targetVenue.longitude)];
            zoom = 15;
          } else if (venuesWithCoords.length === 0) {
            center = [58.603591, 49.668023];
            zoom = 12;
          } else {
            const avgLat = venuesWithCoords.reduce((sum, v) => sum + parseFloat(v.latitude), 0) / venuesWithCoords.length;
            const avgLng = venuesWithCoords.reduce((sum, v) => sum + parseFloat(v.longitude), 0) / venuesWithCoords.length;
            center = [avgLat, avgLng];
            zoom = 12;
          }

          const map = new window.ymaps.Map(mapRef.current, {
            center: center,
            zoom: zoom,
            controls: ['zoomControl', 'fullscreenControl', 'geolocationControl']
          });

          ymapsRef.current = map;

          // Добавляем маркеры
          venuesWithCoords.forEach(venue => {
            try {
              const imageUrl = venue.main_image || (venue.images && venue.images[0] ? venue.images[0].image : null);
              const imageHtml = imageUrl 
                ? `<img src="${imageUrl}" alt="${venue.title}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;" />`
                : '';

              const placemark = new window.ymaps.Placemark(
                [parseFloat(venue.latitude), parseFloat(venue.longitude)],
                {
                  balloonContentHeader: `<div style="font-size: 1.1rem; font-weight: 600; color: #1A4D8F; margin-bottom: 8px;">${venue.title}</div>`,
                  balloonContentBody: `
                    <div style="max-width: 300px;">
                      ${imageHtml}
                      <p style="margin: 8px 0; color: #6B6B6B; font-size: 0.9rem;"><strong>📍 Адрес:</strong> ${venue.address}</p>
                      <p style="margin: 8px 0; color: #6B6B6B; font-size: 0.9rem;"><strong>👥 Вместимость:</strong> ${venue.capacity} человек</p>
                      <p style="margin: 8px 0; color: #1A4D8F; font-size: 1rem; font-weight: 600;"><strong>💰 Цена:</strong> ${venue.price_per_hour} ₽/час</p>
                      ${venue.average_rating > 0 ? `<p style="margin: 8px 0; color: #F5A623; font-weight: 600;">⭐ ${venue.average_rating} (${venue.reviews_count} отзывов)</p>` : ''}
                      <a href="/venues/${venue.id}" style="display: block; width: 100%; margin-top: 12px; padding: 10px 20px; background: linear-gradient(135deg, #1A4D8F 0%, #4DA3FF 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; text-align: center; box-sizing: border-box; transition: transform 0.2s;">Подробнее →</a>
                    </div>
                  `,
                  hintContent: venue.title
                },
                {
                  iconLayout: 'default#image',
                  iconImageHref: 'data:image/svg+xml;base64,' + btoa(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50">
                      <circle cx="25" cy="25" r="20" fill="#1A4D8F" stroke="white" stroke-width="3" opacity="0.9"/>
                      <circle cx="25" cy="25" r="10" fill="white" opacity="0.8"/>
                    </svg>
                  `),
                  iconImageSize: [50, 50],
                  iconImageOffset: [-25, -25]
                }
              );

              // На мобильных - открываем bottom sheet, на десктопе - balloon
              placemark.events.add('click', () => {
                if (isMobile) {
                  placemark.balloon.close(); // Закрываем balloon на мобильных
                  handleVenueClick(venue);
                } else {
                  // На десктопе balloon откроется автоматически
                  placemark.balloon.open();
                }
              });

              placemark.events.add('mouseenter', () => {
                placemark.options.set('iconImageHref', 'data:image/svg+xml;base64,' + btoa(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
                    <circle cx="30" cy="30" r="25" fill="#4DA3FF" stroke="white" stroke-width="4" opacity="0.95"/>
                    <circle cx="30" cy="30" r="12" fill="white" opacity="0.9"/>
                  </svg>
                `));
                placemark.options.set('iconImageSize', [60, 60]);
                placemark.options.set('iconImageOffset', [-30, -30]);
              });

              placemark.events.add('mouseleave', () => {
                placemark.options.set('iconImageHref', 'data:image/svg+xml;base64,' + btoa(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" fill="#1A4D8F" stroke="white" stroke-width="3" opacity="0.9"/>
                    <circle cx="25" cy="25" r="10" fill="white" opacity="0.8"/>
                  </svg>
                `));
                placemark.options.set('iconImageSize', [50, 50]);
                placemark.options.set('iconImageOffset', [-25, -25]);
              });

              map.geoObjects.add(placemark);
              placemarkRefs.current[venue.id] = placemark;

              // Если это целевая площадка, открываем её balloon/bottom sheet
              if (targetVenueId && venue.id === parseInt(targetVenueId)) {
                if (isMobile) {
                  handleVenueClick(venue);
                } else {
                  placemark.balloon.open();
                }
              }
            } catch (err) {
              console.error(`Ошибка добавления маркера для ${venue.title}:`, err);
            }
          });
        } catch (error) {
          console.error('Ошибка инициализации карты:', error);
        }
      });
    } catch (error) {
      console.error('Ошибка при загрузке Яндекс.Карт:', error);
    }
  }, [venues, targetVenueId, isMobile]);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadVenues();
  }, [loadVenues]);

  useEffect(() => {
    if (venues.length > 0) {
      initMap();
    }

    return () => {
      if (ymapsRef.current) {
        ymapsRef.current.destroy();
      }
    };
  }, [venues, initMap]);

  const handleCategoryChange = (categoryId) => {
    setSelectedCategories(prev => {
      const newCategories = prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId];
      return newCategories;
    });
    // Автоматически применяем фильтр при изменении
  };

  const handleClearFilters = () => {
    setSelectedCategories([]);
    // Фильтр применится автоматически через useEffect
  };

  const venuesCount = venues.filter(v => v.latitude && v.longitude).length;

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Загрузка карты...</p>
      </div>
    );
  }

  return (
    <div className="map-page">
      {/* Sidebar с фильтрами - на десктопе слева, на мобильных сверху */}
      <div className="map-sidebar">
        <div className="sidebar-content">
          <h2>🗺️ Карта площадок</h2>
          
          <div className="filter-section">
            <h3>Категории</h3>
            <div className={`categories-list ${isMobile ? 'horizontal-scroll' : ''}`}>
              {categories.map(category => (
                <label key={category.id} className="category-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedCategories.includes(category.id)}
                    onChange={() => handleCategoryChange(category.id)}
                  />
                  <span>{category.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="filter-actions">
            <button onClick={handleClearFilters} className="btn btn-secondary btn-clear">
              🔄 Сбросить фильтры
            </button>
            <div className="venues-count-inline">
              📍 Найдено: <strong>{venuesCount}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Контейнер с картой */}
      <div className="map-container">
        <div ref={mapRef} className="yandex-map" />
        
        {venuesCount === 0 && (
          <div className="map-overlay-message">
            <p>📍 У площадок еще не указаны координаты на карте</p>
            <p>Добавьте координаты через админ-панель Django</p>
          </div>
        )}
      </div>

      {/* Bottom Sheet для мобильных */}
      {isMobile && bottomSheetOpen && selectedVenue && (
        <>
          {/* Overlay */}
          <div 
            className="bottom-sheet-overlay"
            onClick={() => setBottomSheetOpen(false)}
          />
          
          {/* Bottom Sheet */}
          <div
            ref={bottomSheetRef}
            className={`bottom-sheet ${bottomSheetExpanded ? 'expanded' : ''}`}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            {/* Drag Handle */}
            <div className="bottom-sheet-handle">
              <div className="handle-bar"></div>
            </div>

            {/* Content */}
            <div className="bottom-sheet-content">
              {/* Venue Info - Header */}
              <div className="venue-header">
                <h2>{selectedVenue.title}</h2>
                {selectedVenue.average_rating > 0 && (
                  <div className="venue-rating">
                    ⭐ {selectedVenue.average_rating}
                  </div>
                )}
              </div>

              {/* Image */}
              {selectedVenue.main_image || (selectedVenue.images && selectedVenue.images.length > 0) ? (
                <div className="venue-image">
                  <img 
                    src={selectedVenue.main_image || selectedVenue.images[0].image} 
                    alt={selectedVenue.title}
                  />
                </div>
              ) : null}

              {/* Venue Details - Compact */}
              <div className="venue-info">
                <div className="venue-details-compact">
                  <div className="detail-item">
                    <span className="detail-icon">📍</span>
                    <span className="detail-text">{selectedVenue.address}</span>
                  </div>
                  <div className="detail-row">
                    <div className="detail-item">
                      <span className="detail-icon">👥</span>
                      <span className="detail-text">{selectedVenue.capacity} чел.</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">💰</span>
                      <span className="detail-text">{selectedVenue.price_per_hour} ₽/ч</span>
                    </div>
                  </div>
                </div>

                {bottomSheetExpanded && selectedVenue.description && (
                  <div className="venue-description">
                    <p>{selectedVenue.description}</p>
                  </div>
                )}

                <Link 
                  to={`/venues/${selectedVenue.id}`} 
                  className="btn btn-primary btn-block"
                  onClick={() => setBottomSheetOpen(false)}
                >
                  Подробнее и забронировать →
                </Link>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default MapPage;
