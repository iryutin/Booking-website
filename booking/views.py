# Импортируем необходимые компоненты Django REST Framework
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Импортируем утилиты Django для работы с датами и временем
from django.utils import timezone
from datetime import timedelta, date, datetime

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
    def free_slots(self, request, pk=None):
        """
        Получение свободных временных слотов для конкретного стола на выбранную дату
        """
        table = self.get_object()
        date_str = request.query_params.get('date')

        if not date_str:
            return Response({'error': 'Необходимо указать параметр date (YYYY-MM-DD)'}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)

        # Получаем все занятые слоты на эту дату для этого стола
        booked_slots = Booking.objects.filter(
            table=table,
            booking_date=date,
            is_confirmed=True
        ).values_list('time_slot', flat=True)

        # Все возможные слоты
        all_slots = [slot[0] for slot in Booking.TIME_SLOTS]

        # Свободные слоты
        free_slots = [slot for slot in all_slots if slot not in booked_slots]

        return Response({
            'table': table.number,
            'date': date_str,
            'free_slots': free_slots,
            'booked_slots': list(booked_slots)
        })

    @action(detail=False, methods=['post'], url_path='create-booking')
    def create_booking(self, request):
        """
        Создание бронирования с указанием временного слота
        """
        table_number = request.data.get('table_number')
        date_str = request.data.get('date')
        time_slot = request.data.get('time_slot')

        if not all([table_number, date_str, time_slot]):
            return Response(
                {'error': 'Необходимо указать table_number, date и time_slot'},
                status=400
            )

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            table = Table.objects.get(number=table_number, is_active=True)

            # Проверяем допустимость временного слота
            valid_slots = [slot[0] for slot in Booking.TIME_SLOTS]
            if time_slot not in valid_slots:
                return Response(
                    {'error': f'Недопустимый временной слот. Допустимые значения: {valid_slots}'},
                    status=400
                )

            # Проверяем доступность
            if Booking.objects.filter(table=table, booking_date=date, time_slot=time_slot).exists():
                return Response(
                    {'error': 'Этот временной слот уже занят'},
                    status=409
                )

            booking = Booking.objects.create(
                table=table,
                booking_date=date,
                time_slot=time_slot,
                user=request.user if request.user.is_authenticated else None
            )

            # Отправка email с подтверждением
            if request.user.is_authenticated and request.user.email:
                confirmation_url = request.build_absolute_uri(
                    f"/api/tables/confirm-booking/{booking.confirmation_token}/"
                )
                send_mail(
                    'Подтверждение бронирования',
                    f'Подтвердите бронирование стола {table.number} на {date_str} {time_slot}: {confirmation_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )

            return Response({
                'success': True,
                'booking_id': booking.id,
                'table': table.number,
                'date': date_str,
                'time_slot': time_slot,
                'confirmation_url': confirmation_url
            }, status=201)

        except Table.DoesNotExist:
            return Response({'error': 'Стол не найден'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['get'], url_path='available-slots')
    def available_slots(self, request):
        """
        Получение всех доступных слотов для всех столов на выбранную дату
        """
        date_str = request.query_params.get('date')

        if not date_str:
            return Response({'error': 'Необходимо указать параметр date'}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Неверный формат даты'}, status=400)

        # Получаем все бронирования на эту дату
        bookings = Booking.objects.filter(
            booking_date=date,
            is_confirmed=True
        ).values('table', 'time_slot')

        # Создаем структуру данных для ответа
        response_data = {}
        all_slots = [slot[0] for slot in Booking.TIME_SLOTS]

        for table in Table.objects.filter(is_active=True):
            # Занятые слоты для этого стола
            table_bookings = bookings.filter(table=table.id)
            booked_slots = [b['time_slot'] for b in table_bookings]

            # Свободные слоты
            free_slots = [slot for slot in all_slots if slot not in booked_slots]

            response_data[table.number] = {
                'capacity': table.capacity,
                'free_slots': free_slots,
                'booked_slots': booked_slots
            }

        return Response({
            'date': date_str,
            'tables': response_data
        })

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