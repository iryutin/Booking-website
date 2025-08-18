# Импортируем базовый класс для создания моделей Django
from django.db import models
from django.db.models import Q
import uuid
# Импортируем функцию для получения модели пользователя (стандартная или кастомная)
from django.contrib.auth import get_user_model


class Table(models.Model):
    """
    Модель для представления стола в ресторане
    
    В Django модели - это Python классы, которые представляют таблицы в базе данных.
    Каждое поле класса становится колонкой в таблице.
    """
    
    # IntegerField - поле для целых чисел, будет колонкой INTEGER в базе данных
    number = models.IntegerField(
        verbose_name="Номер стола",  # Человекочитаемое название для админки
        help_text="Уникальный номер стола"  # Подсказка в админке
    )
    
    # ImageField - поле для загрузки изображений
    # blank=True - поле может быть пустым в формах
    # null=True - поле может быть NULL в базе данных
    # upload_to="photo" - изображения будут сохраняться в папку media/photo/
    image = models.ImageField(
        blank=True, 
        null=True, 
        upload_to="photo",
        verbose_name="Фото стола",
        help_text="Изображение стола (необязательно)"
    )
    
    # Поле для вместимости стола (количество мест)
    capacity = models.IntegerField(
        verbose_name="Вместимость",
        help_text="Количество мест за столом"
    )
    
    # BooleanField - поле для True/False значений
    # default=True - по умолчанию стол активен
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Доступен ли стол для бронирования"
    )

    class Meta:
        """
        Мета-класс для дополнительных настроек модели
        """
        verbose_name = "Стол"  # Название в единственном числе для админки
        verbose_name_plural = "Столы"  # Название во множественном числе
        ordering = ['number']  # Сортировка по номеру стола

    def __str__(self):
        """
        Метод для строкового представления объекта
        Используется в админке Django и при выводе в консоли
        """
        return f"Стол {self.number} ({self.capacity} мест)"


class Booking(models.Model):
    """
    Модель для представления бронирования стола
    
    Эта модель связывает пользователя, стол и дату бронирования
    """
    
    # DateField - поле для даты (без времени)
    # auto_now_add=True - автоматически устанавливает текущую дату при создании
    booking_date = models.DateField(
        verbose_name="Дата бронирования",
        help_text="На какую дату забронирован стол"
    )
    
    # ForeignKey - связь "многие к одному" с моделью Table
    # on_delete=models.CASCADE - при удалении стола удаляются все его бронирования
    table = models.ForeignKey(
        Table, 
        on_delete=models.CASCADE,
        verbose_name="Стол",
        help_text="Какой стол забронирован"
    )

    # null=True - пользователь может быть не указан (анонимное бронирование)
    # blank=True - поле может быть пустым в формах
    # on_delete=models.SET_NULL - при удалении пользователя бронирование остается, но user становится NULL
    user = models.ForeignKey(
        get_user_model(),  # Получаем модель пользователя (стандартную или кастомную)
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Пользователь",
        help_text="Кто забронировал стол"
    )
    
    # DateTimeField - поле для даты и времени
    # auto_now_add=True - автоматически устанавливает текущее время при создании
    # auto_now=True - автоматически обновляет время при каждом изменении
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Когда было создано бронирование"
    )

    # Статус подтверждения бронирования
    is_confirmed = models.BooleanField(
        default=False,
        verbose_name="Подтверждено",
        help_text="Подтверждено ли бронирование пользователем"
    )

    # Токен для подтверждения бронирования по ссылке
    confirmation_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Токен подтверждения",
        help_text="Уникальный токен для подтверждения бронирования"
    )

    # Время подтверждения
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Подтверждено в",
        help_text="Время, когда бронирование было подтверждено"
    )

    class Meta:
        """
        Мета-класс для дополнительных настроек модели
        """
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        # Сортировка по дате бронирования (сначала новые)
        ordering = ['-booking_date']
        # Уникальность: подтвержденное бронирование для стола на дату только одно
        constraints = [
            models.UniqueConstraint(
                fields=['table', 'booking_date'],
                condition=Q(is_confirmed=True),
                name='unique_confirmed_booking_per_table_date'
            )
        ]

    def __str__(self):
        """
        Метод для строкового представления объекта
        """
        status = "подтверждено" if self.is_confirmed else "неподтверждено"
        if self.user:
            return f"Бронирование {self.user.username} на {self.booking_date} столик {self.table} ({status})"
        else:
            return f"Бронирование на {self.booking_date} столик {self.table} (без пользователя, {status})"

    def is_active_booking(self):
        """
        Метод для проверки, активно ли бронирование
        Бронирование считается активным, если дата не прошла
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.booking_date >= today

    def confirm(self):
        """Подтверждает бронирование, фиксируя время и очищая токен."""
        from django.utils import timezone
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.confirmation_token = None
        self.save(update_fields=["is_confirmed", "confirmed_at", "confirmation_token"])

