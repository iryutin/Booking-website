# Импортируем базовый класс для создания сериализаторов Django REST Framework
from rest_framework import serializers

# Импортируем наши модели для создания сериализаторов
from .models import Table, Booking


class TableSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Table
    
    Сериализатор - это класс Django REST Framework, который:
    1. Преобразует объекты Django (модели) в JSON для отправки клиенту
    2. Преобразует JSON от клиента в объекты Django для сохранения в базе
    
    ModelSerializer - автоматически создает поля на основе модели
    """
    
    class Meta:
        """
        Мета-класс для настройки сериализатора
        
        Meta - специальный класс Python для хранения метаданных
        """
        model = Table  # Указываем модель, для которой создаем сериализатор
        
        # fields - какие поля модели включать в сериализацию
        # '__all__' - включить все поля модели
        # Можно указать конкретные поля: ['number', 'capacity', 'is_active']
        fields = '__all__'
        
        # Можно добавить дополнительные настройки:
        # read_only_fields = ['created_date']  # Поля только для чтения
        # extra_kwargs = {'password': {'write_only': True}}  # Дополнительные параметры для полей


class BookingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Booking
    
    Этот сериализатор автоматически создает поля на основе модели Booking:
    - booking_date: DateField -> JSON строка в формате YYYY-MM-DD
    - table: ForeignKey -> JSON объект с данными стола (или только ID)
    - user: OneToOneField -> JSON объект с данными пользователя (или только ID)
    - created_date: DateTimeField -> JSON строка в формате ISO 8601
    """
    
    class Meta:
        model = Booking
        fields = '__all__'
        
        # Можно настроить более детально:
        # fields = ['id', 'booking_date', 'table', 'user', 'created_date']
        # exclude = ['created_date']  # Исключить определенные поля