from django.test import TestCase

from app.forms import RegisterForm


class RegisterFormTest(TestCase):
    def test_valid_form(self):
        form = RegisterForm(
            data={
                "username": "newuser",
                "email": "test@example.com",
                "password": "securepass123",
                "password_confirm": "securepass123",
            }
        )
        self.assertTrue(form.is_valid())

    # def test_password_mismatch(self):
    #     form = RegisterForm(data={
    #         'username': 'newuser',
    #         'password': 'pass1',
    #         'password_confirm': 'pass2'
    #     })
    #     self.assertFalse(form.is_valid())
    #     self.assertIn('password_confirm', form.errors)
