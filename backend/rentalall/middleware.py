"""
Custom middleware для логирования
"""
import logging

security_logger = logging.getLogger('security')


class SecurityLoggingMiddleware:
    """Middleware для логирования критических событий безопасности"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Логируем неавторизованные попытки доступа
        if response.status_code == 401 and request.user.is_anonymous:
            security_logger.warning(
                f"Unauthorized access attempt: Path={request.path}, "
                f"Method={request.method}, IP={self.get_client_ip(request)}"
            )
        
        # Логируем запрещённые операции
        if response.status_code == 403:
            user_info = request.user.email if request.user.is_authenticated else 'Anonymous'
            security_logger.warning(
                f"Forbidden access attempt: Path={request.path}, "
                f"Method={request.method}, User={user_info}, "
                f"IP={self.get_client_ip(request)}"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Получение IP-адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
