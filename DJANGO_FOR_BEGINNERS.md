# 🐍 Django для начинающих - Основные концепции

Этот файл объясняет основные концепции Django на простых примерах из нашего проекта бронирования столиков.

## 📚 Что такое Django?

**Django** - это веб-фреймворк на Python, который помогает быстро создавать веб-сайты. Он следует архитектуре **MVT** (Model-View-Template).

## 🏗️ Архитектура MVT (Model-View-Template)

### 1. **Model (Модель)** - `models.py`
**Что это:** Описывает структуру данных (таблицы в базе данных)

**Пример из нашего проекта:**
```python
class Table(models.Model):
    number = models.IntegerField()        # Колонка "number" типа INTEGER
    capacity = models.IntegerField()      # Колонка "capacity" типа INTEGER
    is_active = models.BooleanField()     # Колонка "is_active" типа BOOLEAN
```

**Что происходит:**
- Django автоматически создает таблицу `booking_table` в базе данных
- Каждое поле становится колонкой
- Django создает SQL команды за вас

### 2. **View (Представление)** - `views.py`
**Что это:** Логика обработки запросов пользователя

**Пример из нашего проекта:**
```python
def free_dates_page(request):
    """Показывает HTML страницу со свободными датами"""
    return render(request, 'free_dates.html')

class TableViewSet(viewsets.ModelViewSet):
    """API для работы со столами"""
    queryset = Table.objects.filter(is_active=True)
```

**Что происходит:**
- Пользователь заходит на сайт
- Django вызывает соответствующую функцию/класс
- Функция возвращает HTML страницу или данные

### 3. **Template (Шаблон)** - `templates/free_dates.html`
**Что это:** HTML файлы с разметкой страницы

**Пример:**
```html
<h1>🍽️ Свободные даты для бронирования</h1>
<div id="tables-container"></div>
```

## 🔗 URL маршрутизация - `urls.py`

**Что это:** Связывает URL адреса с функциями-представлениями

**Пример:**
```python
urlpatterns = [
    path('', free_dates_page, name='free_dates_page'),           # Главная страница
    path('api/', include(router.urls)),                         # API endpoints
]
```

**Что происходит:**
- Пользователь заходит на `http://127.0.0.1:8000/`
- Django ищет в `urlpatterns` подходящий URL
- Находит `path('', ...)` и вызывает `free_dates_page`

## 🗄️ База данных и ORM

### Что такое ORM?
**ORM** (Object-Relational Mapping) - позволяет работать с базой данных через Python код вместо SQL.

**Примеры:**

```python
# Создание нового стола
table = Table.objects.create(number=1, capacity=4, is_active=True)

# Поиск всех активных столов
active_tables = Table.objects.filter(is_active=True)

# Поиск стола по номеру
table = Table.objects.get(number=1)

# Подсчет количества столов
total_tables = Table.objects.count()
```

## 🔌 API и Django REST Framework

### Что такое API?
**API** - способ обмена данными между приложением и сервером в формате JSON.

**Пример из нашего проекта:**
```python
@action(detail=False, methods=['get'], url_path='all-free-dates')
def all_free_dates(self, request):
    """Получить свободные даты для всех столов"""
    # ... логика получения данных ...
    return Response({
        'tables': tables_data,
        'date_range': {'start': '2024-01-01', 'end': '2024-01-30'}
    })
```

**Что происходит:**
- Пользователь делает запрос на `/api/tables/all-free-dates/`
- Django вызывает функцию `all_free_dates`
- Функция возвращает данные в формате JSON
- Браузер получает данные и отображает их

## 📁 Структура проекта Django

```
pythonProject/
├── booking/                    # Приложение для бронирования
│   ├── models.py              # Модели данных (таблицы)
│   ├── views.py               # Логика обработки запросов
│   ├── serializers.py         # Преобразование данных в JSON
│   └── urls.py                # URL маршруты приложения
├── config/                     # Настройки проекта
│   ├── settings.py            # Основные настройки
│   └── urls.py                # Главные URL маршруты
├── templates/                  # HTML шаблоны
│   └── free_dates.html        # Шаблон главной страницы
└── manage.py                  # Управление проектом
```

## 🚀 Как работает Django приложение?

### 1. **Запрос пользователя**
```
Пользователь заходит на http://127.0.0.1:8000/
```

### 2. **URL маршрутизация**
```
Django ищет в urls.py подходящий URL
Находит path('', free_dates_page, ...)
```

### 3. **Вызов представления**
```
Django вызывает функцию free_dates_page(request)
```

### 4. **Обработка данных**
```
Функция может:
- Получить данные из базы (models.py)
- Обработать данные
- Подготовить данные для шаблона
```

### 5. **Рендеринг шаблона**
```
Функция возвращает render(request, 'free_dates.html')
Django находит HTML файл и отправляет его пользователю
```

## 🎯 Основные команды Django

```bash
# Создать миграции (изменения в моделях)
python manage.py makemigrations

# Применить миграции к базе данных
python manage.py migrate

# Создать суперпользователя (админ)
python manage.py createsuperuser

# Запустить сервер разработки
python manage.py runserver

# Открыть Django shell (интерактивная консоль)
python manage.py shell
```

## 🔍 Полезные ссылки для изучения

- [Официальная документация Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)

## 💡 Советы для новичков

1. **Начните с простого** - сначала разберитесь с моделями и представлениями
2. **Используйте админку** - `python manage.py createsuperuser` создаст админ-панель
3. **Читайте ошибки** - Django дает подробные сообщения об ошибках
4. **Практикуйтесь** - создавайте простые проекты для закрепления знаний
5. **Изучайте код** - смотрите, как работают встроенные приложения Django

## 🎉 Что вы уже знаете!

После изучения этого проекта вы понимаете:
- ✅ Как создавать модели Django
- ✅ Как работать с базой данных через ORM
- ✅ Как создавать API endpoints
- ✅ Как связывать URL с функциями
- ✅ Как отображать HTML страницы
- ✅ Как структурировать Django проект

**Поздравляем! Вы на пути к становлению Django разработчиком! 🚀**
