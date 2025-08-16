# Импортируем необходимые компоненты Django REST Framework
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

# Импортируем утилиты Django для работы с датами и временем
from django.utils import timezone
from datetime import timedelta, date

# Импортируем функцию render для отображения HTML шаблонов
from django.shortcuts import render

# Импортируем наши модели и сериализаторы
from .models import Table, Booking
from .serializers import TableSerializer


def free_dates_page(request):
    """
    Функция-представление (view) для отображения HTML страницы
    
    В Django есть два типа представлений:
    1. Функции (как эта) - простые представления
    2. Классы - более сложные представления с дополнительной функциональностью
    
    request - объект HttpRequest, содержащий информацию о запросе пользователя
    """
    # render() - функция Django для отображения HTML шаблона
    # Первый параметр - объект запроса
    # Второй параметр - путь к HTML файлу (относительно папки templates)
    return render(request, 'free_dates.html')


class TableViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с таблицами через API
    
    ViewSet - это класс Django REST Framework, который автоматически создает
    стандартные операции CRUD (Create, Read, Update, Delete) для модели.
    
    ModelViewSet наследует от ViewSet и добавляет стандартные методы:
    - list() - получить список всех объектов (GET /api/tables/)
    - create() - создать новый объект (POST /api/tables/)
    - retrieve() - получить один объект (GET /api/tables/{id}/)
    - update() - обновить объект (PUT /api/tables/{id}/)
    - destroy() - удалить объект (DELETE /api/tables/{id}/)
    """
    
    # queryset - набор объектов, с которыми работает ViewSet
    # filter() - метод Django ORM для фильтрации объектов
    # is_active=True - показываем только активные столы
    queryset = Table.objects.filter(is_active=True)
    
    # serializer_class - класс для преобразования объектов в JSON и обратно
    serializer_class = TableSerializer
    
    # permission_classes - права доступа к API
    # AllowAny - разрешить доступ всем пользователям (включая анонимных)
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get'], url_path='free-dates')
    def free_dates(self, request, pk=None):
        """
        Кастомное действие (action) для получения свободных дат конкретного стола
        
        @action - декоратор Django REST Framework для создания кастомных endpoints
        detail=True - действие применяется к конкретному объекту (нужен pk)
        methods=['get'] - разрешен только GET запрос
        url_path='free-dates' - URL будет /api/tables/{id}/free-dates/
        
        request - объект запроса
        pk - primary key (ID) стола (автоматически передается Django)
        """
        
        # self.get_object() - метод ViewSet для получения объекта по pk
        table = self.get_object()
        
        # timezone.now() - текущее время с учетом часового пояса
        # .date() - получаем только дату без времени
        today = timezone.now().date()
        
        # Получаем все забронированные даты для конкретного стола
        # filter() - фильтруем записи по условиям
        # table=table - фильтр по столу
        # booking_date__gte=today - дата бронирования больше или равна сегодняшней
        # values_list('booking_date', flat=True) - получаем только даты в виде списка
        booked_dates = Booking.objects.filter(
            table=table,
            booking_date__gte=today
        ).values_list('booking_date', flat=True)

        # Генерируем даты на следующие 30 дней
        # timedelta(days=x) - добавляем x дней к дате
        # list comprehension - создаем список дат
        all_dates = [today + timedelta(days=x) for x in range(30)]
        
        # Фильтруем даты, исключая забронированные
        # [date for date in all_dates if date not in booked_dates] - list comprehension
        free_dates = [date for date in all_dates if date not in booked_dates]

        # Response - класс Django REST Framework для возврата JSON ответа
        return Response({
            'table': table.number,  # Номер стола
            'free_dates': [date.strftime('%Y-%m-%d') for date in free_dates],  # Свободные даты в формате YYYY-MM-DD
            'booked_dates': [date.strftime('%Y-%m-%d') for date in booked_dates]  # Забронированные даты
        })

    @action(detail=False, methods=['get'], url_path='all-free-dates')
    def all_free_dates(self, request):
        """
        Кастомное действие для получения свободных дат всех столов
        
        detail=False - действие применяется ко всем объектам (не нужен pk)
        URL будет /api/tables/all-free-dates/
        """
        
        today = timezone.now().date()
        
        # Получаем все бронирования начиная с сегодня
        # values('table', 'booking_date') - получаем только нужные поля
        all_bookings = Booking.objects.filter(
            booking_date__gte=today
        ).values('table', 'booking_date')
        
        # Генерируем даты на следующие 30 дней
        all_dates = [today + timedelta(days=x) for x in range(30)]
        
        # Создаем словарь для каждого стола
        tables_data = {}
        
        # Проходим по всем активным столам
        for table in Table.objects.filter(is_active=True):
            # Получаем забронированные даты для конкретного стола
            # [b['booking_date'] for b in all_bookings if b['table'] == table.id] - list comprehension
            table_bookings = [b['booking_date'] for b in all_bookings if b['table'] == table.id]
            
            # Находим свободные даты (исключаем забронированные)
            free_dates = [d for d in all_dates if d not in table_bookings]
            
            # Сохраняем информацию о столе
            tables_data[table.number] = {
                'capacity': table.capacity,  # Вместимость
                'free_dates': [date.strftime('%Y-%m-%d') for date in free_dates],  # Свободные даты
                'booked_dates': [date.strftime('%Y-%m-%d') for date in table_bookings]  # Забронированные даты
            }
        
        # Возвращаем структурированный ответ
        return Response({
            'date_range': {
                'start': today.strftime('%Y-%m-%d'),  # Начальная дата
                'end': (today + timedelta(days=29)).strftime('%Y-%m-%d')  # Конечная дата (через 30 дней)
            },
            'tables': tables_data  # Информация о всех столах
        })
