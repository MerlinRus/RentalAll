from rest_framework import generics, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count, Q
import logging
from .models import Category, Venue, VenueImage
from .serializers import (
    CategorySerializer,
    VenueListSerializer,
    VenueDetailSerializer,
    VenueCreateUpdateSerializer,
    VenueImageSerializer
)
from .filters import VenueFilter

# Инициализация логгера для venues
logger = logging.getLogger('venues')


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение: только администратор может создавать/изменять, остальные только читать"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin()


class CategoryListView(generics.ListCreateAPIView):
    """Список всех категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class VenueListView(generics.ListCreateAPIView):
    """Список всех площадок с фильтрацией и поиском"""
    queryset = Venue.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VenueFilter
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['created_at', 'price_per_hour', 'capacity', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VenueCreateUpdateSerializer
        return VenueListSerializer
    
    def get_queryset(self):
        """Оптимизированный queryset с prefetch для избежания N+1 queries"""
        queryset = Venue.objects.all()
        
        # Оптимизация: prefetch related данных
        queryset = queryset.prefetch_related(
            'images',  # Изображения площадки
            'categories',  # Категории
        ).select_related(
            'owner'  # Владелец площадки
        ).annotate(
            # Вычисляем средний рейтинг и количество отзывов на уровне БД
            average_rating=Avg(
                'reviews__rating',
                filter=Q(reviews__is_approved=True)
            ),
            reviews_count=Count(
                'reviews',
                filter=Q(reviews__is_approved=True)
            )
        )
        
        # Если не администратор, показывать только активные площадки
        if not (self.request.user.is_authenticated and self.request.user.is_admin()):
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        venue = serializer.save(owner=self.request.user)
        logger.info(
            f"Venue created: ID={venue.id}, Title={venue.title}, "
            f"Owner={self.request.user.email}, Price={venue.price_per_hour}"
        )


class VenueDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о площадке"""
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Оптимизированный queryset для детальной страницы"""
        return Venue.objects.prefetch_related(
            'images',
            'categories',
            'reviews__user',  # Отзывы с информацией о пользователях
        ).select_related(
            'owner'
        ).annotate(
            average_rating=Avg(
                'reviews__rating',
                filter=Q(reviews__is_approved=True)
            ),
            reviews_count=Count(
                'reviews',
                filter=Q(reviews__is_approved=True)
            )
        )
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VenueCreateUpdateSerializer
        return VenueDetailSerializer
    
    def perform_update(self, serializer):
        venue = serializer.save()
        logger.info(
            f"Venue updated: ID={venue.id}, Title={venue.title}, "
            f"Editor={self.request.user.email}"
        )
    
    def perform_destroy(self, instance):
        logger.warning(
            f"Venue deleted: ID={instance.id}, Title={instance.title}, "
            f"Deleted by={self.request.user.email}"
        )
        instance.delete()


class VenueImageUploadView(APIView):
    """Загрузка фотографий для площадки"""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    def post(self, request, venue_id):
        try:
            venue = Venue.objects.get(id=venue_id)
        except Venue.DoesNotExist:
            return Response(
                {'error': 'Площадка не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверка прав (только админ или владелец)
        if not (request.user.is_admin() or venue.owner == request.user):
            return Response(
                {'error': 'Нет прав для загрузки фотографий'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = VenueImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(venue=venue)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, venue_id, image_id):
        try:
            venue = Venue.objects.get(id=venue_id)
            image = VenueImage.objects.get(id=image_id, venue=venue)
        except (Venue.DoesNotExist, VenueImage.DoesNotExist):
            return Response(
                {'error': 'Изображение не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверка прав
        if not (request.user.is_admin() or venue.owner == request.user):
            return Response(
                {'error': 'Нет прав для удаления фотографий'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        image.delete()
        return Response(
            {'message': 'Изображение удалено'},
            status=status.HTTP_204_NO_CONTENT
        )

