from abc import ABC

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class BasePaymentTestCase(ABC, TestCase):
    """Base test case for payment-related tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
