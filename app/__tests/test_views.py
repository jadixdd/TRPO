from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from app.models import Category, Expense


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_login_success(self):
        response = self.client.post(
            reverse("app:login"), {"username": "testuser", "password": "12345"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("app:dashboard"))

    def test_login_fail(self):
        response = self.client.post(
            reverse("app:login"), {"username": "testuser", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверное имя пользователя или пароль")

    def test_logout(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("app:logout"))
        self.assertRedirects(response, reverse("app:login"))


class ExpensesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.category = Category.objects.create(user=self.user, name="Еда")
        self.client.login(username="testuser", password="12345")

    def test_expenses_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("app:expenses"))
        self.assertRedirects(
            response, f"{reverse('app:login')}?next={reverse('app:expenses')}"
        )

    def test_add_expense(self):
        response = self.client.post(
            reverse("app:expenses"),
            {
                "action": "add_expense",
                "amount": "99.99",
                "category": self.category.id,
                "date": "2025-04-05",
                "description": "Тест",
            },
            follow=True,
        )
        self.assertContains(response, "Трата успешно добавлена")
        self.assertTrue(Expense.objects.filter(amount=Decimal("99.99")).exists())

    def test_edit_expense(self):
        expense = Expense.objects.create(
            user=self.user, amount=100, category=self.category, date="2025-04-01"
        )
        response = self.client.post(
            reverse("app:expenses"),
            {
                "action": "edit_expense",
                "expense_id": expense.id,
                "amount": "150.00",
                "category": self.category.id,
                "date": "2025-04-02",
            },
        )
        expense.refresh_from_db()
        self.assertEqual(expense.amount, Decimal("150.00"))

    def test_delete_expense(self):
        expense = Expense.objects.create(user=self.user, amount=100, date="2025-04-01")
        response = self.client.post(
            reverse("app:expenses"),
            {"action": "delete_expense", "expense_id": expense.id},
        )
        self.assertFalse(Expense.objects.filter(id=expense.id).exists())
