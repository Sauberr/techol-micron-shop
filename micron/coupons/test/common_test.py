from datetime import timedelta

from coupons.models.coupon import Coupon
from django.test import TestCase
from django.utils import timezone


class BaseCouponTestCase(TestCase):
    def setUp(self):
        # Create a test coupon with validity dates from the current moment
        self.now = timezone.now()
        self.coupon = Coupon.objects.create(
            code='TESTCODE2025',
            valid_from=self.now,
            valid_to=self.now + timedelta(days=30),
            discount=25,
            active=True
        )