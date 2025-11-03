from django import forms
from django.contrib.auth.models import User


# Простая форма регистрации, использующая стандартного пользователя Django.
# Для реального проекта, использующего email как username, может потребоваться
# кастомная модель User, но для старта подойдет и эта.
class RegisterForm(forms.ModelForm):
    # Добавляем поле для подтверждения пароля, которое не сохраняется в модели
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(),
        }
        labels = {
            "username": "Имя пользователя",
            "email": "Email",
            "password": "Пароль",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Устанавливаем пароль с помощью set_password для корректного хеширования
        user.set_password(self.cleaned_data["password"])
        # Используем email как username, если вы хотите аутентификацию по email
        # В вашем views.py вы уже используете email для аутентификации,
        # но для стандартной модели User нужно сохранять username.
        # Если вы хотите использовать email как основной идентификатор, вам нужно
        # настроить кастомную модель User или использовать username=email при регистрации.
        # Для простоты, пока оставим username как отдельное поле.
        if commit:
            user.save()
        return user
