from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from user_account.test.common_test import BaseViewTestCase


User = get_user_model()


class ChangePasswordViewTestCase(BaseViewTestCase):
    path_name = 'user_account:password_change'
    template_name = 'user_account/password/password_change.html'
    title = '| Change Password'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='testuser', password='swagerfeed123')
        self.client.login(username='testuser', password='swagerfeed123')

    def test_change_password(self):
        response = self.client.post(reverse(self.path_name), {
            'old_password': 'swagerfeed123',
            'new_password1': 'swagerfeed123P0',
            'new_password2': 'swagerfeed123P0',
        })

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('swagerfeed123P0'))