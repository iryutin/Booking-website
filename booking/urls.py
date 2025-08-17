# Импортируем функции для создания URL маршрутов
from django.urls import path, include
from booking.apps import BookingConfig
# Импортируем DefaultRouter для автоматического создания URL для ViewSet
from rest_framework.routers import DefaultRouter

# Импортируем наши представления (views)
from .views import TableViewSet, free_dates_page

app_name = BookingConfig.name
# Создаем экземпляр роутера для автоматической генерации URL
# DefaultRouter автоматически создает стандартные URL для ViewSet:
# - /api/tables/ - список всех столов (GET) и создание (POST)
# - /api/tables/{id}/ - получение, обновление, удаление конкретного стола
# - /api/tables/{id}/free-dates/ - наше кастомное действие
# - /api/tables/all-free-dates/ - наше кастомное действие
router = DefaultRouter()

# Регистрируем ViewSet в роутере
# Первый параметр - префикс URL (будет /api/tables/)
# Второй параметр - класс ViewSet
router.register(r'tables', TableViewSet)

# urlpatterns - список URL маршрутов Django
# Django проходит по этому списку сверху вниз и ищет первый подходящий URL
urlpatterns = [
    # Пустой путь '' - главная страница сайта
    # free_dates_page - функция-представление, которая будет вызвана
    # name='free_dates_page' - имя для обратной генерации URL в шаблонах
    path('', free_dates_page, name='free_dates_page'),
    
    # /api/ - префикс для всех API endpoints
    # include(router.urls) - включает все URL, созданные роутером
    # Это создаст /api/tables/, /api/tables/{id}/, /api/tables/{id}/free-dates/ и т.д.
    path('api/', include(router.urls)),
]