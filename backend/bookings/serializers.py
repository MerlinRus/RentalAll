from rest_framework import serializers
from django.utils import timezone
from .models import Booking, Payment
from venues.serializers import VenueListSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения бронирования"""
    venue_details = VenueListSerializer(source='venue', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_be_cancelled = serializers.SerializerMethodField()
    has_review = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = (
            'id', 'user', 'user_name', 'venue', 'venue_details', 'date_start',
            'date_end', 'status', 'status_display', 'total_price', 'created_at',
            'can_be_cancelled', 'has_review'
        )
        read_only_fields = ('id', 'user', 'total_price', 'created_at', 'status')
    
    def get_can_be_cancelled(self, obj):
        return obj.can_be_cancelled()
    
    def get_has_review(self, obj):
        """Проверка, есть ли отзыв для этого бронирования"""
        return hasattr(obj, 'review')


class BookingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания бронирования"""
    
    class Meta:
        model = Booking
        fields = ('venue', 'date_start', 'date_end')
    
    def validate(self, attrs):
        """Валидация данных бронирования"""
        date_start = attrs.get('date_start')
        date_end = attrs.get('date_end')
        venue = attrs.get('venue')
        
        # Проверка, что дата начала не в прошлом
        if date_start < timezone.now():
            raise serializers.ValidationError({
                'date_start': 'Дата начала не может быть в прошлом'
            })
        
        # Проверка, что дата окончания после даты начала
        if date_end <= date_start:
            raise serializers.ValidationError({
                'date_end': 'Дата окончания должна быть после даты начала'
            })
        
        # Проверка минимальной длительности (например, 1 час)
        duration = date_end - date_start
        if duration.total_seconds() < 3600:
            raise serializers.ValidationError({
                'date_end': 'Минимальная длительность бронирования - 1 час'
            })
        
        # Проверка доступности площадки
        if not Booking.check_availability(venue, date_start, date_end):
            raise serializers.ValidationError({
                'venue': 'Площадка недоступна на выбранное время'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Создание бронирования с автоматическим расчетом цены"""
        booking = Booking(**validated_data)
        booking.total_price = booking.calculate_total_price()
        booking.save()
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статуса бронирования"""
    
    class Meta:
        model = Booking
        fields = ('status',)
    
    def validate_status(self, value):
        """Валидация смены статуса"""
        instance = self.instance
        
        # Проверка возможности отмены
        if value == 'cancelled':
            if not instance.can_be_cancelled():
                raise serializers.ValidationError(
                    'Это бронирование не может быть отменено'
                )
        
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежа"""
    booking_details = BookingSerializer(source='booking', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'booking', 'booking_details', 'amount', 'status',
            'status_display', 'payment_method', 'payment_method_display', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания платежа"""
    
    class Meta:
        model = Payment
        fields = ('booking', 'payment_method')
    
    def validate_booking(self, value):
        """Проверка, что бронирование может быть оплачено"""
        if value.status == 'cancelled':
            raise serializers.ValidationError('Отменённое бронирование не может быть оплачено')
        
        # Проверка, что нет успешного платежа
        if value.payments.filter(status='paid').exists():
            raise serializers.ValidationError('Бронирование уже оплачено')
        
        return value
    
    def create(self, validated_data):
        """Создание платежа с суммой из бронирования"""
        booking = validated_data['booking']
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            payment_method=validated_data.get('payment_method', 'card'),
            status='pending'
        )
        return payment

