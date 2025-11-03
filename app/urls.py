from django.urls import path

from . import views

urlpatterns = [
    # Главная — редирект
    path("", views.home, name="home"),
    # Аутентификация
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.CustomLogoutView.as_view(next_page="login"), name="logout"),
    # Основные страницы (требуют авторизации)
    path("dashboard/", views.dashboard, name="dashboard"),
    path("expenses/", views.expenses, name="expenses"),
    path("reports/", views.reports, name="reports"),
    path("categories/", views.categories, name="categories"),
    path("settings/", views.settings, name="settings"),
]
