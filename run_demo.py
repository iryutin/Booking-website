#!/usr/bin/env python
"""
Скрипт для быстрого запуска демо-версии системы бронирования
"""

import os
import sys
import django
from datetime import date, timedelta

def setup_django():
    """Настройка Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def create_demo_data():
    """Создание демо-данных"""
    from booking.models import Table, Booking
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    print("🍽️ Создание демо-данных для системы бронирования...")
    
    # Создаем демо-пользователя
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@restaurant.com',
            'first_name': 'Демо',
            'last_name': 'Пользователь'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print("✅ Создан демо-пользователь: demo/demo123")
    
    # Создаем демо-столы
    tables_data = [
        {'number': 1, 'capacity': 2, 'is_active': True},
        {'number': 2, 'capacity': 4, 'is_active': True},
        {'number': 3, 'capacity': 6, 'is_active': True},
        {'number': 4, 'capacity': 8, 'is_active': True},
        {'number': 5, 'capacity': 2, 'is_active': True},
        {'number': 6, 'capacity': 4, 'is_active': True},
    ]
    
    for table_data in tables_data:
        table, created = Table.objects.get_or_create(
            number=table_data['number'],
            defaults=table_data
        )
        if created:
            print(f"✅ Создан стол {table.number} ({table.capacity} мест)")
    
    # Создаем демо-бронирования
    today = date.today()
    
    demo_bookings = [
        (1, today + timedelta(days=1)),      # Стол 1 завтра
        (1, today + timedelta(days=3)),      # Стол 1 через 3 дня
        (2, today + timedelta(days=2)),      # Стол 2 послезавтра
        (3, today + timedelta(days=5)),      # Стол 3 через 5 дней
        (4, today + timedelta(days=7)),      # Стол 4 через неделю
        (5, today + timedelta(days=10)),     # Стол 5 через 10 дней
        (6, today + timedelta(days=15)),     # Стол 6 через 15 дней
    ]
    
    for table_num, booking_date in demo_bookings:
        table = Table.objects.get(number=table_num)
        booking, created = Booking.objects.get_or_create(
            table=table,
            booking_date=booking_date,
            defaults={'user': user}
        )
        if created:
            print(f"✅ Забронирован стол {table_num} на {booking_date.strftime('%d.%m.%Y')}")
    
    print(f"\n🎉 Демо-данные созданы успешно!")
    print(f"📊 Статистика:")
    print(f"   • Столов: {Table.objects.count()}")
    print(f"   • Бронирований: {Booking.objects.count()}")
    print(f"   • Пользователей: {User.objects.count()}")

def main():
    """Основная функция"""
    print("🚀 Запуск системы бронирования столиков...")
    
    try:
        setup_django()
        create_demo_data()
        
        print("\n🌐 Система готова к работе!")
        print("📱 Откройте браузер и перейдите по адресу: http://127.0.0.1:8000/")
        print("🔌 API доступен по адресу: http://127.0.0.1:8000/api/")
        print("\n💡 Для запуска сервера выполните: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("💡 Убедитесь, что вы находитесь в директории проекта")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())


