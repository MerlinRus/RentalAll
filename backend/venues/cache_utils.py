"""
Утилиты для работы с кэшированием рейтингов площадок
"""
from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg, Count, Q
import logging

logger = logging.getLogger('venues')


def get_cache_key(venue_id, metric='rating'):
    """Генерирует ключ кэша для площадки"""
    return f'venue:{venue_id}:{metric}'


def get_venue_rating_from_cache(venue_id):
    """
    Получает рейтинг и количество отзывов из кэша.
    Если не найдено - вычисляет и кэширует.
    """
    cache_key = get_cache_key(venue_id, 'rating_data')
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        logger.debug(f'Cache HIT: venue_id={venue_id}')
        return cached_data
    
    # Если кэш пустой - вычисляем
    logger.debug(f'Cache MISS: venue_id={venue_id}, calculating...')
    from venues.models import Venue
    
    try:
        venue = Venue.objects.filter(id=venue_id).annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        ).first()
        
        if venue:
            rating_data = {
                'average_rating': float(venue.average_rating) if venue.average_rating else 0.0,
                'reviews_count': venue.reviews_count
            }
            
            # Кэшируем на 1 час
            ttl = settings.CACHE_TTL.get('venue_rating', 3600)
            cache.set(cache_key, rating_data, ttl)
            logger.info(f'Cached rating for venue_id={venue_id}: {rating_data}')
            
            return rating_data
    except Exception as e:
        logger.error(f'Error calculating rating for venue_id={venue_id}: {e}')
    
    return {'average_rating': 0.0, 'reviews_count': 0}


def invalidate_venue_rating_cache(venue_id):
    """Инвалидирует кэш рейтинга для площадки"""
    cache_key = get_cache_key(venue_id, 'rating_data')
    cache.delete(cache_key)
    logger.info(f'Invalidated cache for venue_id={venue_id}')


def invalidate_all_venue_caches():
    """Инвалидирует весь кэш (для критических обновлений)"""
    cache.clear()
    logger.warning('Cleared all cache')
