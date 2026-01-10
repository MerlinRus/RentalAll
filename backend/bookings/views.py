from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Booking, Payment
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение: владелец объекта или администратор"""
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Booking):
            return obj.user == request.user or request.user.is_admin()
        elif isinstance(obj, Payment):
            return obj.booking.user == request.user or request.user.is_admin()
        return False


class BookingListCreateView(generics.ListCreateAPIView):
    """Список бронирований пользователя и создание нового"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        """Пользователи видят только свои бронирования, админы - все"""
        if self.request.user.is_admin():
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Создание бронирования с возвратом полного объекта"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(user=request.user)
        
        # Возвращаем полный объект через BookingSerializer
        output_serializer = BookingSerializer(booking)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о бронировании"""
    queryset = Booking.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer


class BookingCancelView(APIView):
    """Отмена бронирования"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        
        # Проверка прав
        self.check_object_permissions(request, booking)
        
        # Проверка возможности отмены
        if not booking.can_be_cancelled():
            return Response(
                {'error': 'Это бронирование не может быть отменено'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )


class BookingConfirmView(APIView):
    """Подтверждение бронирования (только для администраторов)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_admin():
            return Response(
                {'error': 'Только администратор может подтверждать бронирования'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking = get_object_or_404(Booking, pk=pk)
        
        if booking.status != 'pending':
            return Response(
                {'error': 'Можно подтверждать только бронирования в статусе "Ожидает подтверждения"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )


class PaymentListCreateView(generics.ListCreateAPIView):
    """Список платежей и создание нового"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """Пользователи видят только свои платежи, админы - все"""
        if self.request.user.is_admin():
            return Payment.objects.all()
        return Payment.objects.filter(booking__user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Создание платежа"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Проверка, что пользователь - владелец бронирования
        booking = serializer.validated_data['booking']
        if booking.user != request.user and not request.user.is_admin():
            return Response(
                {'error': 'Вы можете оплачивать только свои бронирования'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment = serializer.save()
        
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )


class PaymentDetailView(generics.RetrieveAPIView):
    """Детальная информация о платеже"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]


class PaymentProcessView(APIView):
    """Обработка платежа (имитация оплаты для диплома)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        
        # Проверка прав
        if payment.booking.user != request.user and not request.user.is_admin():
            return Response(
                {'error': 'Нет прав для обработки этого платежа'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if payment.status == 'paid':
            return Response(
                {'error': 'Платеж уже оплачен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Имитация успешной оплаты
        payment.status = 'paid'
        payment.save()
        
        # Автоматически подтверждаем бронирование после оплаты
        if payment.booking.status == 'pending':
            payment.booking.status = 'confirmed'
            payment.booking.save()
        
        return Response(
            {
                'message': 'Платеж успешно обработан',
                'payment': PaymentSerializer(payment).data
            },
            status=status.HTTP_200_OK
        )


class OccupiedSlotsView(APIView):
    """Получение занятых временных слотов для площадки на определенную дату"""
    permission_classes = []  # Доступно всем
    
    def get(self, request):
        venue_id = request.query_params.get('venue')
        date_str = request.query_params.get('date')  # Формат: YYYY-MM-DD
        
        if not venue_id or not date_str:
            return Response(
                {'error': 'Параметры venue и date обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime, timedelta
            from django.db.models import Q
            
            # Парсим дату
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Получаем все бронирования для площадки на эту дату
            # Исключаем только отмененные
            bookings = Booking.objects.filter(
                venue_id=venue_id,
                date_start__date=date
            ).exclude(
                status='cancelled'
            ).values('date_start', 'date_end')
            
            # Формируем список занятых слотов в формате "HH:MM - HH:MM"
            # Конвертируем из UTC в локальное время
            from zoneinfo import ZoneInfo
            
            # Определяем локальную временную зону
            local_tz = ZoneInfo('Europe/Moscow')  # UTC+3 Москва
            
            occupied_slots = []
            for booking in bookings:
                # Конвертируем UTC время в локальное
                start_local = booking['date_start'].astimezone(local_tz)
                end_local = booking['date_end'].astimezone(local_tz)
                
                start_time = start_local.strftime('%H:%M')
                end_time = end_local.strftime('%H:%M')
                occupied_slots.append(f"{start_time} - {end_time}")
            
            return Response({
                'date': date_str,
                'venue': venue_id,
                'occupied_slots': occupied_slots
            })
            
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

