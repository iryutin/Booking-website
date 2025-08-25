from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from user.forms import CustomUserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib import messages

User = get_user_model()


class RegisterView(CreateView):
    """Представление для регистрации пользователей"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('booking:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Автоматически входим в систему после регистрации
        login(self.request, self.object)
        messages.success(self.request, f'Добро пожаловать, {self.object.email}!')
        return response

    def form_invalid(self, form):
        # Добавляем сообщения об ошибках
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """Кастомное представление для входа"""
    template_name = 'user/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('booking:home')

    def get_success_url(self):
        """Перенаправление после успешного входа"""
        return self.next_page or reverse_lazy('booking:home')


class CustomLogoutView(LogoutView):
    """Кастомное представление для выхода"""
    next_page = reverse_lazy('booking:home')