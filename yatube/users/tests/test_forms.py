from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UsersFormsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_form_signup(self):
        users_count = User.objects.count()
        form_data = {
            'username': 'TestUser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='TestUser').exists())
