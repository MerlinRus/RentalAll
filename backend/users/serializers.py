from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'phone', 'role', 'date_joined', 'is_active')
        read_only_fields = ('id', 'date_joined', 'role')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Подтверждение пароля')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'full_name', 'phone')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            phone=validated_data.get('phone', ''),
            role='user'
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'phone', 'role', 'date_joined')
        read_only_fields = ('id', 'username', 'role', 'date_joined')


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True, label='Подтверждение нового пароля')
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs

