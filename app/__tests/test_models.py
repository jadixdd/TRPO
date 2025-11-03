from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Category, Expense
from decimal import Decimal
from datetime import date


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    def test_category_creation(self):
        cat = Category.objects.create(user=self.user, name="Еда")
        self.assertEqual(str(cat), "Еда")
        self.assertEqual(cat.user, self.user)

    def test_unique_together(self):
        Category.objects.create(user=self.user, name="Транспорт")
        with self.assertRaises(Exception):  # IntegrityError
            Category.objects.create(user=self.user, name="Транспорт")


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(user=self.user, name="Еда")

    def test_expense_creation(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('150.50'),
            description="Обед",
            date=date.today()
        )
        self.assertEqual(expense.amount, Decimal('150.50'))
        self.assertTrue(expense.category is not None)

    def test_expense_without_category(self):
        expense = Expense.objects.create(
            user=self.user,
            amount=Decimal('100'),
            date=date.today()
        )
        self.assertIsNone(expense.category)

    def test_ordering(self):
        Expense.objects.create(user=self.user, amount=100, date=date(2025, 1, 1))
        Expense.objects.create(user=self.user, amount=200, date=date(2025, 1, 3))
        Expense.objects.create(user=self.user, amount=300, date=date(2025, 1, 2))
        expenses = Expense.objects.all()
        self.assertEqual(expenses[0].date, date(2025, 1, 3))