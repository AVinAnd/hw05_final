from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('TestUser')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_exist_not_auth_user(self):
        """страницы доступны неавторизированному пользователю"""
        field_urls = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.guest_client.get(field).status_code, expected_value)

    def test_exist_auth_user(self):
        """страницы доступны авторизированному пользователю"""
        field_urls = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.auth_client.get(field).status_code, expected_value)

    def test_urls_templates(self):
        """url использует правильный шаблон html"""
        field_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.auth_client.get(field), expected_value)

    def test_views_templates(self):
        """view функции используют правильные html шаблоны"""
        fields = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for path, expected_template in fields.items():
            with self.subTest(path=path):
                self.assertTemplateUsed(
                    self.auth_client.get(path), expected_template)
