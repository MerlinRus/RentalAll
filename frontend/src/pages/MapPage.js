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
  const targetVenueId = searchParams.get('venue'); // ID площадки из URL параметра
  const mapRef = useRef(null);
  const ymapsRef = useRef(null);
  const placemarkRefs = useRef({}); // Хранилище ссылок на маркеры

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
          // Уничтожаем старую карту если есть
          if (ymapsRef.current) {
            ymapsRef.current.destroy();
          }

          // Находим центр карты (среднее по всем координатам)
          const venuesWithCoords = venues.filter(v => v.latitude && v.longitude);
          
          let center, zoom;
          
          // Если указан конкретный venue ID, центрируем карту на нём
          const targetVenue = targetVenueId ? venuesWithCoords.find(v => v.id === parseInt(targetVenueId)) : null;
          
          if (targetVenue) {
            center = [parseFloat(targetVenue.latitude), parseFloat(targetVenue.longitude)];
            zoom = 15; // Больший zoom для конкретной площадки
          } else if (venuesWithCoords.length === 0) {
            // Если нет координат, центр Кирова
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

          // Добавляем маркеры для каждой площадки
          venuesWithCoords.forEach(venue => {
            try {
              // Формируем HTML для балуна с фото
              const imageUrl = venue.main_image || (venue.images && venue.images[0] ? venue.images[0].image : null);
              const imageHtml = imageUrl 
                ? `<img src="${imageUrl}" alt="${venue.title}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;" />`
                : '';

              const placemark = new window.ymaps.Placemark(
                [parseFloat(venue.latitude), parseFloat(venue.longitude)],
                {
                  balloonContentHeader: `<div style="font-size: 1.1rem; font-weight: 600; color: #1A4D8F; margin-bottom: 8px;">${venue.title}</div>`,
                  balloonContentBody: `
                    <div style="max-width: 280px;">
                      ${imageHtml}
                      <p style="margin: 8px 0; color: #6B6B6B; font-size: 0.9rem;"><strong>Адрес:</strong> ${venue.address}</p>
                      <p style="margin: 8px 0; color: #6B6B6B; font-size: 0.9rem;"><strong>Вместимость:</strong> ${venue.capacity} человек</p>
                      <p style="margin: 8px 0; color: #1A4D8F; font-size: 1rem; font-weight: 600;"><strong>Цена:</strong> ${venue.price_per_hour} ₽/час</p>
                      ${venue.average_rating > 0 ? `<p style="margin: 8px 0; color: #4DA3FF; font-weight: 600;">⭐ ${venue.average_rating} (${venue.reviews_count} отзывов)</p>` : ''}
                      <a href="/venues/${venue.id}" style="display: inline-block; margin-top: 10px; padding: 8px 16px; background: linear-gradient(135deg, #1A4D8F 0%, #4DA3FF 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 600; text-align: center;">Подробнее →</a>
                    </div>
                  `,
                  hintContent: venue.title
                },
                {
                  // Круглый маркер с кастомной иконкой
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

              // Добавляем анимацию при наведении
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
              
              // Сохраняем ссылку на маркер
              placemarkRefs.current[venue.id] = placemark;
            } catch (err) {
              console.error(`Ошибка добавления маркера для ${venue.title}:`, err);
            }
          });

          // Если указан targetVenueId, открываем балун автоматически
          if (targetVenueId && placemarkRefs.current[targetVenueId]) {
            setTimeout(() => {
              placemarkRefs.current[targetVenueId].balloon.open();
            }, 500); // Небольшая задержка для корректной инициализации
          }
        } catch (err) {
          console.error('Ошибка при создании карты:', err);
        }
      });
    } catch (err) {
      console.error('Ошибка ymaps.ready:', err);
    }
  }, [venues, targetVenueId]);

  const handleCategoryToggle = (categoryId) => {
    setSelectedCategories(prev => {
      if (prev.includes(categoryId)) {
        return prev.filter(id => id !== categoryId);
      } else {
        return [...prev, categoryId];
      }
    });
  };

  const handleApplyFilters = () => {
    setLoading(true);
    loadVenues();
  };

  const handleResetFilters = () => {
    setSelectedCategories([]);
    setLoading(true);
    // Перезагружаем без фильтров
    setTimeout(() => {
      loadVenues();
    }, 100);
  };

  // Инициализация при загрузке
  useEffect(() => {
    loadCategories();
    loadVenues();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Загрузка Yandex Maps API когда появляются площадки
  useEffect(() => {
    // Загружаем Yandex Maps API только если есть площадки
    if (venues.length === 0) return;

    const loadYandexMaps = () => {
      if (!window.ymaps) {
        const script = document.createElement('script');
        script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU';
        script.async = true;
        script.onload = () => {
          initMap();
        };
        script.onerror = () => {
          console.error('Ошибка загрузки Yandex Maps API');
        };
        document.body.appendChild(script);
      } else {
        initMap();
      }
    };

    const timeoutId = setTimeout(() => {
      loadYandexMaps();
    }, 100);

    // Cleanup
    return () => {
      clearTimeout(timeoutId);
      if (ymapsRef.current) {
        try {
          ymapsRef.current.destroy();
        } catch (err) {
          console.error('Ошибка при уничтожении карты:', err);
        }
        ymapsRef.current = null;
      }
    };
  }, [venues, initMap]);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="map-page">
      <div className="map-sidebar">
        <div className="sidebar-content">
          <h2>Фильтры</h2>
          
          <div className="filter-section">
            <h3>Категории</h3>
            <div className="categories-list">
              {categories.map(category => (
                <label key={category.id} className="category-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedCategories.includes(category.id)}
                    onChange={() => handleCategoryToggle(category.id)}
                  />
                  <span>{category.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="filter-actions">
            <button className="btn btn-primary" onClick={handleApplyFilters}>
              Применить
            </button>
            <button className="btn btn-secondary" onClick={handleResetFilters}>
              Сбросить
            </button>
          </div>

          <div className="venues-count">
            Найдено площадок: <strong>{venues.filter(v => v.latitude && v.longitude).length}</strong>
          </div>
        </div>
      </div>

      <div className="map-container">
        <div ref={mapRef} className="yandex-map"></div>
        {venues.length > 0 && venues.filter(v => v.latitude && v.longitude).length === 0 && (
          <div className="map-overlay-message">
            <p>📍 У площадок еще не указаны координаты на карте</p>
            <p>Добавьте координаты через админ-панель Django</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapPage;

