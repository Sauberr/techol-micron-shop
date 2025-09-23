from django.contrib.auth import get_user_model

from user_account.test.common_test import BaseViewTestCase
from http import HTTPStatus

from django.contrib import auth
from django.core import mail
from django.urls import reverse


User = get_user_model()


class ResetPasswordViewTestCase(BaseViewTestCase):
    path_name = 'user_account:password_reset'
    template_name = 'user_account/password/password_reset.html'
    title = '| Reset Password'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='swagerfeed', password='swagerfeed123',
                                             email='swagerfeed@gmail.com')

    def test_user_login(self):
        login_path = reverse('user_account:login')
        response = self.client.post(login_path, {'username': 'swagerfeed', 'password': 'swagerfeed123'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_password_reset(self):
        response = self.client.post(self.path, {'email': 'swagerfeed@gmail.com'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual((len(mail.outbox)), 1)
        self.assertIn('swagerfeed@gmail.com', mail.outbox[0].to)