from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма для создания пользователя с email как username"""

    # Убираем поле username, так как используем email
    username = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    # Делаем email обязательным и добавляем валидацию
    email = forms.EmailField(
        required=True,
        help_text='Обязательное поле. Введите корректный email адрес.'
    )

    # Добавляем поля для дополнительной информации
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text='Необязательное поле. Формат: +7XXXXXXXXXX'
    )

    name = forms.CharField(
        max_length=15,
        required=False,
        help_text='Необязательное поле. Ваше имя'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'phone_number', 'name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем username из отображения
        if 'username' in self.fields:
            del self.fields['username']

        # Настройка полей
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'autofocus': True
        })

        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX'
        })

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        # Устанавливаем username равным email
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
        return user