from http import HTTPStatus

from django.contrib.auth import get_user_model

from user_account.test.common_test import BaseViewTestCase

User = get_user_model()


class UserRegistrationViewTestCase(BaseViewTestCase):
    path_name = 'user_account:registration'
    template_name = 'user_account/registration/registration.html'
    title = '| Registration'

    def setUp(self):
        super().setUp()
        self.data = {
            'first_name': 'swager', 'last_name': 'feed',
            'username': 'swager', 'email': 'swagerfeed@gmail.com',
            'password1': '123456789pP', 'password2': '123456789pP'
        }

    def test_user_registration_post_error(self):
        User.objects.create(username=self.data['username'])
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'A user with that username already exists.', html=True)



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


class ChangePasswordViewTestCase(TestCase):
    path_name = 'user_account:password_change'
    template_name = 'user_account/password/password_change.html'
    title = '| Change Password'

    def setUp(self):
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