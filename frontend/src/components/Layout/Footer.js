import React from 'react';
import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3>RentalAll</h3>
          <p>Агрегатор площадок для проведения мероприятий</p>
        </div>
        
        <div className="footer-section">
          <h4>О проекте</h4>
          <p>Дипломная работа</p>
          <p>"Разработка информационной системы-агрегатора для бронирования площадок и аудиторий для мероприятий"</p>
        </div>
        
        <div className="footer-section">
          <h4>Технологии</h4>
          <ul>
            <li>React</li>
            <li>Django REST Framework</li>
            <li>PostgreSQL</li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; {currentYear} RentalAll. Все права защищены.</p>
      </div>
    </footer>
  );
};

export default Footer;

