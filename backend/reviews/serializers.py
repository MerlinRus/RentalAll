from rest_framework import serializers
from .models import Review
from bookings.models import Booking


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения отзыва"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    venue_title = serializers.CharField(source='venue.title', read_only=True)
    booking_id = serializers.IntegerField(source='booking.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Review
        fields = (
            'id', 'user', 'user_name', 'user_username', 'venue', 'venue_title',
            'booking', 'booking_id', 'rating', 'comment', 'created_at', 'is_approved'
        )
        read_only_fields = ('id', 'user', 'created_at', 'is_approved')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отзыва"""
    
    class Meta:
        model = Review
        fields = ('booking', 'rating', 'comment')
    
    def validate(self, attrs):
        """Валидация создания отзыва"""
        user = self.context['request'].user
        booking = attrs.get('booking')
        
        # Проверка, что бронирование принадлежит пользователю
        if booking.user != user:
            raise serializers.ValidationError({
                'booking': 'Это не ваше бронирование'
            })
        
        # Проверка, что бронирование завершено (дата окончания прошла)
        from django.utils import timezone
        if booking.date_end > timezone.now():
            raise serializers.ValidationError({
                'booking': 'Вы можете оставить отзыв только после завершения бронирования'
            })
        
        # Проверка, что для этого бронирования ещё нет отзыва
        if hasattr(booking, 'review'):
            raise serializers.ValidationError({
                'booking': 'Вы уже оставляли отзыв для этого бронирования'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Создание отзыва"""
        booking = validated_data['booking']
        return Review.objects.create(
            user=self.context['request'].user,
            venue=booking.venue,  # Автоматически берём площадку из бронирования
            **validated_data
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления отзыва"""
    
    class Meta:
        model = Review
        fields = ('rating', 'comment')


class ReviewApproveSerializer(serializers.ModelSerializer):
    """Сериализатор для одобрения отзыва (администратором)"""
    
    class Meta:
        model = Review
        fields = ('is_approved',)

