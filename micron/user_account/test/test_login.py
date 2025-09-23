from http import HTTPStatus

from django.contrib.auth import get_user_model

from user_account.test.common_test import BaseViewTestCase
from django.contrib import auth

User = get_user_model()


class UserLoginViewTestCase(BaseViewTestCase):
    path_name = 'user_account:login'
    template_name = 'user_account/login.html'
    title = '| Login'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='swagerfeed', password='swagerfeed123')

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.path, {'username': 'swagerfeed', 'password': 'swagerfeed123'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.path, {'username': 'swagerfeed', 'password': 'swagerfeed1234'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)