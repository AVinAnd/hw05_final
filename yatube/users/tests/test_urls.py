from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('User')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_exist_not_auth_user(self):
        """страницы доступны неавторизированному пользователю"""
        field_urls = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/<uidb64>/<token>/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.guest_client.get(field).status_code, expected_value)

    def test_exist_auth_user(self):
        """страницы доступны авторизированному пользователю"""
        field_urls = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/<uidb64>/<token>/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.OK.value,
            '/auth/password_change/done/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.auth_client.get(field).status_code, expected_value)

    def test_redirect_not_auth_user(self):
        """страницы редиректят неавторизированного пользователя"""
        field_urls = {
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
                '/auth/login/?next=/auth/password_change/done/',
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertRedirects(
                    self.guest_client.get(field, follow=True), expected_value)

    def test_urls_templates(self):
        """url использует правильный шаблон html"""
        field_urls = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.auth_client.get(field), expected_value)
