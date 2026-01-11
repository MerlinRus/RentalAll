"""
Custom throttling classes для критических операций
"""
from rest_framework.throttling import UserRateThrottle


class BookingRateThrottle(UserRateThrottle):
    """
    Ограничение частоты создания бронирований
    10 бронирований в час на пользователя
    """
    scope = 'booking'


class ReviewRateThrottle(UserRateThrottle):
    """
    Ограничение частоты создания отзывов
    5 отзывов в день на пользователя
    """
    scope = 'review'
