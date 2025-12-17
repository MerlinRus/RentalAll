import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { toast } from 'react-toastify';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user, refreshUser } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    email: user?.email || ''
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password2: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authAPI.updateProfile(formData);
      await refreshUser();
      toast.success('Профиль обновлён');
      setEditMode(false);
    } catch (error) {
      toast.error('Ошибка обновления профиля');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.new_password2) {
      toast.error('Пароли не совпадают');
      return;
    }

    setLoading(true);

    try {
      await authAPI.changePassword(passwordData);
      toast.success('Пароль изменён');
      setPasswordData({
        old_password: '',
        new_password: '',
        new_password2: ''
      });
    } catch (error) {
      toast.error(error.response?.data?.old_password || 'Ошибка смены пароля');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="profile-page">
      <div className="container">
        <h1>Профиль пользователя</h1>

        <div className="profile-section">
          <h2>Информация о профиле</h2>
          {!editMode ? (
            <div className="profile-info">
              <div className="info-item">
                <span className="label">Имя пользователя:</span>
                <span className="value">{user.username}</span>
              </div>
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{user.email}</span>
              </div>
              <div className="info-item">
                <span className="label">ФИО:</span>
                <span className="value">{user.full_name || '—'}</span>
              </div>
              <div className="info-item">
                <span className="label">Телефон:</span>
                <span className="value">{user.phone || '—'}</span>
              </div>
              <div className="info-item">
                <span className="label">Роль:</span>
                <span className="value">{user.role === 'admin' ? 'Администратор' : 'Пользователь'}</span>
              </div>
              <div className="info-item">
                <span className="label">Дата регистрации:</span>
                <span className="value">{new Date(user.date_joined).toLocaleDateString('ru-RU')}</span>
              </div>
              <button 
                onClick={() => setEditMode(true)} 
                className="btn btn-primary"
              >
                Редактировать
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="profile-form">
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              <div className="form-group">
                <label>ФИО</label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              <div className="form-group">
                <label>Телефон</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Сохранение...' : 'Сохранить'}
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setEditMode(false)}
                  disabled={loading}
                >
                  Отмена
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="profile-section">
          <h2>Смена пароля</h2>
          <form onSubmit={handlePasswordSubmit} className="profile-form">
            <div className="form-group">
              <label>Старый пароль</label>
              <input
                type="password"
                name="old_password"
                value={passwordData.old_password}
                onChange={handlePasswordChange}
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label>Новый пароль</label>
              <input
                type="password"
                name="new_password"
                value={passwordData.new_password}
                onChange={handlePasswordChange}
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label>Подтверждение нового пароля</label>
              <input
                type="password"
                name="new_password2"
                value={passwordData.new_password2}
                onChange={handlePasswordChange}
                required
                disabled={loading}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Изменение...' : 'Изменить пароль'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

