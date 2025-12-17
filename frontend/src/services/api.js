import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Создание экземпляра axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена к запросам
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок и обновления токена
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если получили 401 и это не запрос на обновление токена
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/users/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Если обновление токена не удалось, выходим
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API методы для пользователей
export const authAPI = {
  login: (username, password) =>
    api.post('/users/login/', { username, password }),
  
  register: (userData) =>
    api.post('/users/register/', userData),
  
  getProfile: () =>
    api.get('/users/profile/'),
  
  updateProfile: (userData) =>
    api.patch('/users/profile/', userData),
  
  changePassword: (passwordData) =>
    api.post('/users/change-password/', passwordData),
};

// API методы для площадок
export const venuesAPI = {
  getAll: (params) =>
    api.get('/venues/', { params }),
  
  getById: (id) =>
    api.get(`/venues/${id}/`),
  
  create: (venueData) =>
    api.post('/venues/', venueData),
  
  update: (id, venueData) =>
    api.patch(`/venues/${id}/`, venueData),
  
  delete: (id) =>
    api.delete(`/venues/${id}/`),
  
  uploadImage: (venueId, imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return api.post(`/venues/${venueId}/images/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  deleteImage: (venueId, imageId) =>
    api.delete(`/venues/${venueId}/images/${imageId}/`),
};

// API методы для категорий
export const categoriesAPI = {
  getAll: () =>
    api.get('/venues/categories/'),
  
  create: (categoryData) =>
    api.post('/venues/categories/', categoryData),
};

// API методы для бронирований
export const bookingsAPI = {
  getAll: () =>
    api.get('/bookings/'),
  
  getById: (id) =>
    api.get(`/bookings/${id}/`),
  
  create: (bookingData) =>
    api.post('/bookings/', bookingData),
  
  update: (id, bookingData) =>
    api.patch(`/bookings/${id}/`, bookingData),
  
  cancel: (id) =>
    api.post(`/bookings/${id}/cancel/`),
  
  confirm: (id) =>
    api.post(`/bookings/${id}/confirm/`),
  
  delete: (id) =>
    api.delete(`/bookings/${id}/`),
  
  getOccupiedSlots: (venueId, date) =>
    api.get(`/bookings/occupied-slots/`, { params: { venue: venueId, date } }),
};

// API методы для платежей
export const paymentsAPI = {
  getAll: () =>
    api.get('/bookings/payments/'),
  
  getById: (id) =>
    api.get(`/bookings/payments/${id}/`),
  
  create: (paymentData) =>
    api.post('/bookings/payments/', paymentData),
  
  process: (id) =>
    api.post(`/bookings/payments/${id}/process/`),
};

// API методы для отзывов
export const reviewsAPI = {
  getAll: (params) =>
    api.get('/reviews/', { params }),
  
  getUserReviews: () =>
    api.get('/reviews/my/'),
  
  getPending: () =>
    api.get('/reviews/pending/'),
  
  create: (reviewData) =>
    api.post('/reviews/create/', reviewData),
  
  update: (id, reviewData) =>
    api.patch(`/reviews/${id}/`, reviewData),
  
  delete: (id) =>
    api.delete(`/reviews/${id}/`),
  
  approve: (id) =>
    api.post(`/reviews/${id}/approve/`),
  
  disapprove: (id) =>
    api.post(`/reviews/${id}/disapprove/`),
};

export default api;

