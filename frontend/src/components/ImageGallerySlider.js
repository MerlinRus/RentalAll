import React, { useState } from 'react';
import './ImageGallerySlider.css';

const ImageGallerySlider = ({ images, venueName }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!images || images.length === 0) {
    return (
      <div className="image-gallery-slider">
        <div className="no-image-large">
          <span className="no-image-icon">🏢</span>
          <p>Нет изображений</p>
        </div>
      </div>
    );
  }

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const goToImage = (index) => {
    setCurrentIndex(index);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowLeft') prevImage();
    if (e.key === 'ArrowRight') nextImage();
    if (e.key === 'Escape') setIsFullscreen(false);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <>
      <div className="image-gallery-slider">
        {/* Главное изображение */}
        <div className="main-image-container">
          <div className="main-image-wrapper">
            <img
              src={images[currentIndex].image}
              alt={`${venueName} - фото ${currentIndex + 1}`}
              className="main-image"
              onClick={toggleFullscreen}
            />
            
            {/* Кнопка полноэкранного режима */}
            <button 
              className="fullscreen-btn" 
              onClick={toggleFullscreen}
              aria-label="Открыть в полноэкранном режиме"
            >
              🔍
            </button>

            {/* Счетчик фотографий */}
            <div className="image-count-badge">
              {currentIndex + 1} / {images.length}
            </div>

            {/* Навигация */}
            {images.length > 1 && (
              <>
                <button
                  className="slider-nav-btn prev-btn"
                  onClick={prevImage}
                  aria-label="Предыдущее фото"
                >
                  ‹
                </button>
                <button
                  className="slider-nav-btn next-btn"
                  onClick={nextImage}
                  aria-label="Следующее фото"
                >
                  ›
                </button>
              </>
            )}
          </div>
        </div>

        {/* Миниатюры */}
        {images.length > 1 && (
          <div className="thumbnails-container">
            <div className="thumbnails-wrapper">
              {images.map((img, index) => (
                <div
                  key={index}
                  className={`thumbnail ${index === currentIndex ? 'active' : ''}`}
                  onClick={() => goToImage(index)}
                >
                  <img src={img.image} alt={`Миниатюра ${index + 1}`} />
                  {index === currentIndex && <div className="thumbnail-overlay" />}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Полноэкранный режим */}
      {isFullscreen && (
        <div 
          className="fullscreen-modal" 
          onClick={toggleFullscreen}
          onKeyDown={handleKeyDown}
          tabIndex={0}
        >
          <div className="fullscreen-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={toggleFullscreen}>
              ✕
            </button>
            
            <img
              src={images[currentIndex].image}
              alt={`${venueName} - фото ${currentIndex + 1}`}
              className="fullscreen-image"
            />

            {images.length > 1 && (
              <>
                <button
                  className="fullscreen-nav-btn prev-btn"
                  onClick={prevImage}
                >
                  ‹
                </button>
                <button
                  className="fullscreen-nav-btn next-btn"
                  onClick={nextImage}
                >
                  ›
                </button>

                {/* Индикаторы */}
                <div className="fullscreen-indicators">
                  {images.map((_, index) => (
                    <button
                      key={index}
                      className={`fs-indicator ${index === currentIndex ? 'active' : ''}`}
                      onClick={() => goToImage(index)}
                    />
                  ))}
                </div>

                {/* Счетчик */}
                <div className="fullscreen-counter">
                  {currentIndex + 1} / {images.length}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ImageGallerySlider;

