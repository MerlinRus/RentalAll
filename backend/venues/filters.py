import django_filters
from .models import Venue


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Фильтр для множественного выбора по числовым значениям"""
    pass


class VenueFilter(django_filters.FilterSet):
    """Фильтры для поиска площадок"""
    
    title = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    capacity_min = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte', label='Мин. вместимость')
    capacity_max = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte', label='Макс. вместимость')
    price_min = django_filters.NumberFilter(field_name='price_per_hour', lookup_expr='gte', label='Мин. цена')
    price_max = django_filters.NumberFilter(field_name='price_per_hour', lookup_expr='lte', label='Макс. цена')
    address = django_filters.CharFilter(lookup_expr='icontains', label='Адрес')
    category = NumberInFilter(field_name='categories', lookup_expr='in', label='Категории')
    is_active = django_filters.BooleanFilter(label='Активна')
    
    class Meta:
        model = Venue
        fields = ['title', 'capacity_min', 'capacity_max', 'price_min', 'price_max', 'address', 'category', 'is_active']

