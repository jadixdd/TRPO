# app/__tests/test_urls.py
from django.test import TestCase
from django.urls import reverse, resolve
from app.urls import urlpatterns  # ← импортируем urlpatterns

class URLsTest(TestCase):
    def test_dashboard_url(self):
        url = reverse('dashboard')
        # Ищем в urlpatterns
        for pattern in urlpatterns:
            if pattern.name == 'dashboard':
                self.assertEqual(resolve(url).func, pattern.callback)
                break
        else:
            self.fail("URL 'dashboard' not found")

    def test_expenses_url(self):
        url = reverse('expenses')
        for pattern in urlpatterns:
            if pattern.name == 'expenses':
                self.assertEqual(resolve(url).func, pattern.callback)
                break
        else:
            self.fail("URL 'expenses' not found")