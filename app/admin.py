# app/admin.py
from django.contrib import admin

from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "amount", "date"]
    list_filter = ["category", "date"]
    search_fields = ["description"]
