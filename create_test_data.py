#!/usr/bin/env python
"""
Скрипт для создания тестовых данных для системы бронирования
Запускать через: python manage.py shell < create_test_data.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from booking.models import Table, Booking
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_data():
    print("Создание тестовых данных...")
    
    # Создаем тестового пользователя
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Создан пользователь: {user.username}")
    else:
        print(f"Пользователь {user.username} уже существует")
    
    # Создаем тестовые столы
    tables_data = [
        {'number': 1, 'capacity': 2, 'is_active': True},
        {'number': 2, 'capacity': 4, 'is_active': True},
        {'number': 3, 'capacity': 6, 'is_active': True},
        {'number': 4, 'capacity': 8, 'is_active': True},
        {'number': 5, 'capacity': 2, 'is_active': True},
    ]
    
    created_tables = []
    for table_data in tables_data:
        table, created = Table.objects.get_or_create(
            number=table_data['number'],
            defaults=table_data
        )
        if created:
            print(f"Создан стол: {table}")
        else:
            print(f"Стол {table} уже существует")
        created_tables.append(table)
    
    # Создаем тестовые бронирования
    today = date.today()
    
    # Бронируем несколько дат для разных столов
    test_bookings = [
        (1, today + timedelta(days=1)),      # Стол 1 завтра
        (1, today + timedelta(days=3)),      # Стол 1 через 3 дня
        (2, today + timedelta(days=2)),      # Стол 2 послезавтра
        (3, today + timedelta(days=5)),      # Стол 3 через 5 дней
        (4, today + timedelta(days=7)),      # Стол 4 через неделю
        (5, today + timedelta(days=10)),     # Стол 5 через 10 дней
    ]
    
    for table_num, booking_date in test_bookings:
        table = Table.objects.get(number=table_num)
        booking, created = Booking.objects.get_or_create(
            table=table,
            booking_date=booking_date,
            defaults={'user': user}
        )
        if created:
            print(f"Создано бронирование: {booking}")
        else:
            print(f"Бронирование на {booking_date} для стола {table_num} уже существует")
    
    print("\nТестовые данные созданы успешно!")
    print(f"Всего столов: {Table.objects.count()}")
    print(f"Всего бронирований: {Booking.objects.count()}")
    print(f"Пользователей: {User.objects.count()}")

if __name__ == '__main__':
    create_test_data()
