from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewApproveSerializer
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение: владелец отзыва или администратор"""
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_admin()


class ReviewListView(generics.ListAPIView):
    """Список всех одобренных отзывов или отзывов конкретной площадки"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Фильтрация отзывов"""
        queryset = Review.objects.filter(is_approved=True)
        
        # Фильтр по площадке
        venue_id = self.request.query_params.get('venue', None)
        if venue_id is not None:
            queryset = queryset.filter(venue_id=venue_id)
        
        # Фильтр по рейтингу
        rating = self.request.query_params.get('rating', None)
        if rating is not None:
            queryset = queryset.filter(rating=rating)
        
        return queryset


class UserReviewListView(generics.ListAPIView):
    """Список отзывов текущего пользователя"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


class ReviewCreateView(generics.CreateAPIView):
    """Создание нового отзыва"""
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        return Response(
            {
                'message': 'Отзыв успешно создан и отправлен на модерацию',
                'review': ReviewSerializer(review).data
            },
            status=status.HTTP_201_CREATED
        )


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация об отзыве"""
    queryset = Review.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewUpdateSerializer
        return ReviewSerializer
    
    def update(self, request, *args, **kwargs):
        """При обновлении отзыва, сбрасываем одобрение"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # Сбрасываем одобрение при редактировании
        instance.is_approved = False
        self.perform_update(serializer)
        
        return Response(ReviewSerializer(instance).data)


class ReviewApproveView(APIView):
    """Одобрение отзыва (только для администраторов)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_admin():
            return Response(
                {'error': 'Только администратор может одобрять отзывы'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = True
        review.save()
        
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_200_OK
        )


class ReviewDisapproveView(APIView):
    """Отклонение отзыва (только для администраторов)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_admin():
            return Response(
                {'error': 'Только администратор может отклонять отзывы'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = False
        review.save()
        
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_200_OK
        )


class PendingReviewsView(generics.ListAPIView):
    """Список отзывов на модерации (только для администраторов)"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_admin():
            return Review.objects.none()
        return Review.objects.filter(is_approved=False)

