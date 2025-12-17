from rest_framework import serializers
from .models import Category, Venue, VenueImage


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    
    class Meta:
        model = Category
        fields = ('id', 'name')


class VenueImageSerializer(serializers.ModelSerializer):
    """Сериализатор для фотографий площадки"""
    
    class Meta:
        model = VenueImage
        fields = ('id', 'image', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')


class VenueListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка площадок (краткая информация)"""
    categories = CategorySerializer(many=True, read_only=True)
    images = VenueImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = (
            'id', 'title', 'capacity', 'price_per_hour', 'address',
            'latitude', 'longitude',  # Добавлены координаты для карты
            'main_image', 'images', 'categories', 'average_rating', 'reviews_count', 'is_active'
        )
    
    def get_main_image(self, obj):
        """Получить первое изображение площадки"""
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
        return None
    
    def get_average_rating(self, obj):
        """Получить средний рейтинг"""
        return obj.get_average_rating()
    
    def get_reviews_count(self, obj):
        """Получить количество отзывов"""
        return obj.get_reviews_count()


class VenueDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о площадке"""
    categories = CategorySerializer(many=True, read_only=True)
    images = VenueImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    
    class Meta:
        model = Venue
        fields = (
            'id', 'owner', 'owner_name', 'title', 'description', 'capacity',
            'price_per_hour', 'address', 'latitude', 'longitude', 'created_at',
            'is_active', 'categories', 'images', 'average_rating', 'reviews_count'
        )
        read_only_fields = ('id', 'created_at', 'owner')
    
    def get_average_rating(self, obj):
        """Получить средний рейтинг"""
        return obj.get_average_rating()
    
    def get_reviews_count(self, obj):
        """Получить количество отзывов"""
        return obj.get_reviews_count()


class VenueCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления площадки"""
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Venue
        fields = (
            'title', 'description', 'capacity', 'price_per_hour', 'address',
            'latitude', 'longitude', 'is_active', 'category_ids'
        )
    
    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        venue = Venue.objects.create(**validated_data)
        
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            venue.categories.set(categories)
        
        return venue
    
    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if category_ids is not None:
            categories = Category.objects.filter(id__in=category_ids)
            instance.categories.set(categories)
        
        return instance

