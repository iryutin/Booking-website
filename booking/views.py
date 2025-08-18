# Импортируем необходимые компоненты Django REST Framework
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Импортируем утилиты Django для работы с датами и временем
from django.utils import timezone
from datetime import timedelta, date

# Импортируем функцию render для отображения HTML шаблонов
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings

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
            booking_date__gte=today,
            is_confirmed=True
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
            booking_date__gte=today,
            is_confirmed=True
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

    @action(detail=False, methods=['post'], url_path='create-booking')
    def create_booking(self, request):
        """
        Кастомное действие для создания бронирования
        
        detail=False - действие применяется ко всем объектам (не нужен pk)
        methods=['post'] - разрешен только POST запрос
        URL будет /api/tables/create-booking/
        """
        
        # Получаем данные из запроса
        table_number = request.data.get('table_number')
        booking_date_str = request.data.get('booking_date')
        
        # Валидация данных
        if not table_number or not booking_date_str:
            return Response(
                {
                    'error': 'Необходимо указать table_number и booking_date',
                    'required_fields': ['table_number', 'booking_date']
                },
                status=400
            )
        
        # Требуем авторизацию и наличие email для отправки подтверждения
        if not request.user.is_authenticated or not getattr(request.user, 'email', None):
            return Response(
                {
                    'error': 'Для бронирования войдите в систему и укажите email в профиле.'
                },
                status=401
            )

        try:
            # Парсим дату
            from datetime import datetime
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    'error': 'Неверный формат даты. Используйте YYYY-MM-DD',
                    'example': '2024-01-15'
                },
                status=400
            )
        
        try:
            # Получаем стол по номеру
            from django.shortcuts import get_object_or_404
            table = get_object_or_404(Table, number=table_number, is_active=True)
            
            # Проверяем, не забронирован ли уже стол на эту дату
            if Booking.objects.filter(table=table, booking_date=booking_date).exists():
                return Response(
                    {
                        'error': f'Стол №{table_number} уже забронирован на {booking_date_str}',
                        'table_number': table_number,
                        'booking_date': booking_date_str
                    },
                    status=409
                )
            
            # Создаем бронирование (неподтвержденное, с токеном)
            booking = Booking.objects.create(
                table=table,
                booking_date=booking_date,
                user=request.user if request.user.is_authenticated else None,
                is_confirmed=False
            )
            
            # Отправляем письмо с подтверждением, если у пользователя есть email
            try:
                recipient = None
                if request.user.is_authenticated and request.user.email:
                    recipient = request.user.email
                if recipient:
                    confirmation_url = request.build_absolute_uri(
                        f"/api/tables/confirm-booking/{booking.confirmation_token}/"
                    )
                    subject = "Подтверждение бронирования стола"
                    message = (
                        f"Здравствуйте!\n\n"
                        f"Вы запросили бронирование стола №{table.number} на дату {booking_date_str}.\n"
                        f"Для подтверждения перейдите по ссылке: {confirmation_url}\n\n"
                        f"Если вы не делали этот запрос, просто проигнорируйте письмо."
                    )
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient],
                        fail_silently=True,
                    )
            except Exception:
                pass

            # Возвращаем успешный ответ
            return Response(
                {
                    'success': True,
                    'message': f'Стол №{table_number} успешно забронирован на {booking_date_str}',
                    'booking': {
                        'id': booking.id,
                        'table_number': table_number,
                        'booking_date': booking_date_str,
                        'user': request.user.username if request.user.is_authenticated else 'Анонимный пользователь',
                        'created_date': booking.created_date.isoformat(),
                        'is_confirmed': booking.is_confirmed,
                        'confirmation_token': str(booking.confirmation_token),
                        'confirmation_url': request.build_absolute_uri(
                            f"/api/tables/confirm-booking/{booking.confirmation_token}/"
                        )
                    }
                },
                status=201
            )
            
        except Exception as e:
            return Response(
                {
                    'error': f'Ошибка при создании бронирования: {str(e)}',
                    'table_number': table_number,
                    'booking_date': booking_date_str
                },
                status=500
            )

    @action(detail=False, methods=['get'], url_path=r'confirm-booking/(?P<token>[0-9a-f\-]{36})')
    def confirm_booking(self, request, token=None):
        """
        Подтверждение бронирования по токену.
        Доступно по GET, чтобы можно было переходить по ссылке из письма без JS.
        """
        try:
            booking = get_object_or_404(Booking, confirmation_token=token)
            # Если уже подтверждено
            if booking.is_confirmed:
                return Response({
                    'success': True,
                    'message': 'Бронирование уже подтверждено',
                    'booking_id': booking.id
                })

            # Подтверждаем
            try:
                booking.confirm()
            except IntegrityError:
                return Response({
                    'error': 'Эта дата уже подтверждена для выбранного стола другим пользователем'
                }, status=409)
            return Response({
                'success': True,
                'message': 'Бронирование успешно подтверждено',
                'booking_id': booking.id
            })
        except Exception as e:
            return Response({'error': f'Не удалось подтвердить бронирование: {str(e)}'}, status=400)

class HomePageView(TemplateView):
    """Главная страница ресторана"""
    template_name = 'home.html'

class AboutRestaurantView(TemplateView):
    """Страница 'О ресторане'"""
    template_name = 'about.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    """Личный кабинет пользователя"""
    template_name = 'profile.html'
    login_url = '/user/login/'  # URL для перенаправления неавторизованных пользователей

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings'] = Booking.objects.filter(user=self.request.user)
        return context