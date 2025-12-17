import React, { useState, useEffect } from 'react';
import { venuesAPI, categoriesAPI } from '../services/api';
import VenueCard from '../components/VenueCard';
import './VenueListPage.css';

const VenueListPage = () => {
  const [venues, setVenues] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    capacity_min: '',
    capacity_max: '',
    price_min: '',
    price_max: ''
  });

  useEffect(() => {
    loadCategories();
    loadVenues();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await categoriesAPI.getAll();
      // Обрабатываем разные форматы ответа API
      const data = response.data;
      if (Array.isArray(data)) {
        setCategories(data);
      } else if (data.results && Array.isArray(data.results)) {
        setCategories(data.results);
      } else {
        setCategories([]);
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
      setCategories([]);
    }
  };

  const loadVenues = async (filterParams = {}) => {
    setLoading(true);
    try {
      const response = await venuesAPI.getAll(filterParams);
      const data = response.data;
      // Обрабатываем разные форматы ответа API
      if (Array.isArray(data)) {
        setVenues(data);
      } else if (data.results && Array.isArray(data.results)) {
        setVenues(data.results);
      } else {
        setVenues([]);
      }
    } catch (error) {
      console.error('Ошибка загрузки площадок:', error);
      setVenues([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const params = {};
    
    if (filters.search) params.search = filters.search;
    if (filters.category) params.category = filters.category;
    if (filters.capacity_min) params.capacity_min = filters.capacity_min;
    if (filters.capacity_max) params.capacity_max = filters.capacity_max;
    if (filters.price_min) params.price_min = filters.price_min;
    if (filters.price_max) params.price_max = filters.price_max;
    
    loadVenues(params);
  };

  const handleReset = () => {
    setFilters({
      search: '',
      category: '',
      capacity_min: '',
      capacity_max: '',
      price_min: '',
      price_max: ''
    });
    loadVenues();
  };

  if (loading && venues.length === 0) {
    return <div className="loading">Загрузка площадок...</div>;
  }

  return (
    <div className="venue-list-page">
      <div className="container">
        <h1>Каталог площадок</h1>

        <div className="filters-section">
          <form onSubmit={handleSearch} className="filters-form">
            <div className="filter-group">
              <input
                type="text"
                name="search"
                placeholder="Поиск по названию или адресу"
                value={filters.search}
                onChange={handleFilterChange}
              />
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <select
                  name="category"
                  value={filters.category}
                  onChange={handleFilterChange}
                >
                  <option value="">Все категории</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <input
                  type="number"
                  name="capacity_min"
                  placeholder="Вместимость от"
                  value={filters.capacity_min}
                  onChange={handleFilterChange}
                  min="0"
                />
              </div>

              <div className="filter-group">
                <input
                  type="number"
                  name="capacity_max"
                  placeholder="Вместимость до"
                  value={filters.capacity_max}
                  onChange={handleFilterChange}
                  min="0"
                />
              </div>
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <input
                  type="number"
                  name="price_min"
                  placeholder="Цена от (₽/час)"
                  value={filters.price_min}
                  onChange={handleFilterChange}
                  min="0"
                />
              </div>

              <div className="filter-group">
                <input
                  type="number"
                  name="price_max"
                  placeholder="Цена до (₽/час)"
                  value={filters.price_max}
                  onChange={handleFilterChange}
                  min="0"
                />
              </div>
            </div>

            <div className="filter-actions">
              <button type="submit" className="btn btn-primary">
                Применить фильтры
              </button>
              <button type="button" className="btn btn-secondary" onClick={handleReset}>
                Сбросить
              </button>
            </div>
          </form>
        </div>

        {venues.length === 0 ? (
          <div className="no-results">
            <p>Площадки не найдены</p>
          </div>
        ) : (
          <div className="venues-grid">
            {venues.map(venue => (
              <VenueCard key={venue.id} venue={venue} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VenueListPage;

