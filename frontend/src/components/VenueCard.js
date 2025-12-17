import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './VenueCard.css';

const VenueCard = ({ venue }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  // Получаем все изображения или используем заглушку
  const images = venue.images && venue.images.length > 0 
    ? venue.images 
    : venue.main_image 
    ? [{ image: venue.main_image }] 
    : [];

  const hasMultipleImages = images.length > 1;

  const nextImage = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const goToImage = (e, index) => {
    e.preventDefault();
    e.stopPropagation();
    setCurrentImageIndex(index);
  };

  return (
    <Link to={`/venues/${venue.id}`} className="venue-card">
      <div className="venue-image-container">
        {images.length > 0 ? (
          <>
            <div className="venue-image">
              <img 
                src={images[currentImageIndex].image} 
                alt={`${venue.title} - фото ${currentImageIndex + 1}`} 
              />
            </div>
            
            {hasMultipleImages && (
              <>
                {/* Кнопки навигации */}
                <button 
                  className="image-nav-btn prev-btn" 
                  onClick={prevImage}
                  aria-label="Предыдущее фото"
                >
                  ‹
                </button>
                <button 
                  className="image-nav-btn next-btn" 
                  onClick={nextImage}
                  aria-label="Следующее фото"
                >
                  ›
                </button>
                
                {/* Индикаторы */}
                <div className="image-indicators">
                  {images.map((_, index) => (
                    <button
                      key={index}
                      className={`indicator ${index === currentImageIndex ? 'active' : ''}`}
                      onClick={(e) => goToImage(e, index)}
                      aria-label={`Перейти к фото ${index + 1}`}
                    />
                  ))}
                </div>

                {/* Счетчик фотографий */}
                <div className="image-counter">
                  {currentImageIndex + 1} / {images.length}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="no-image">Нет изображения</div>
        )}
      </div>

      <div className="venue-content">
        <h3>{venue.title}</h3>
        <div className="venue-info">
          <span className="venue-capacity">👥 {venue.capacity} чел.</span>
          <span className="venue-price">{venue.price_per_hour} ₽/час</span>
        </div>
        <p className="venue-address">📍 {venue.address}</p>
        
        {venue.categories && venue.categories.length > 0 && (
          <div className="venue-categories">
            {venue.categories.map(cat => (
              <span key={cat.id} className="category-tag">{cat.name}</span>
            ))}
          </div>
        )}
        
        {venue.average_rating > 0 && (
          <div className="venue-rating">
            ⭐ {venue.average_rating} ({venue.reviews_count} отзывов)
          </div>
        )}

        {/* Кнопка "Посмотреть на карте" */}
        {venue.latitude && venue.longitude && (
          <Link 
            to={`/map?venue=${venue.id}`} 
            className="map-link-btn"
            onClick={(e) => e.stopPropagation()}
          >
            🗺️ Посмотреть на карте
          </Link>
        )}
      </div>
    </Link>
  );
};

export default VenueCard;

