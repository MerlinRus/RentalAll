import React from 'react';
import { Link } from 'react-router-dom';
import './NotFoundPage.css';

const NotFoundPage = () => {
  return (
    <div className="not-found-page">
      <div className="container">
        <h1>404</h1>
        <h2>Страница не найдена</h2>
        <p>К сожалению, запрашиваемая вами страница не существует.</p>
        <Link to="/" className="btn btn-primary">
          Вернуться на главную
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;

