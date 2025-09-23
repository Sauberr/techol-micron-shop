from datetime import timedelta

from coupons.models.coupon import Coupon
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from coupons.test.common_test import BaseCouponTestCase


class CouponModelTestCase(BaseCouponTestCase):
    def test_coupon_creation(self):
        """Test basic coupon creation with valid data"""
        self.assertEqual(self.coupon.code, 'TESTCODE2025')
        self.assertEqual(self.coupon.discount, 25)
        self.assertTrue(self.coupon.active)
        self.assertEqual(str(self.coupon), 'TESTCODE2025')

    def test_coupon_unique_code(self):
        """Test that coupon code must be unique"""
        with self.assertRaises(Exception):
            Coupon.objects.create(
                code='TESTCODE2025',  # Duplicate code
                valid_from=self.now,
                valid_to=self.now + timedelta(days=30),
                discount=30,
                active=True
            )

    def test_coupon_discount_validators(self):
        """Test discount value validators"""
        # Test discount below 0
        with self.assertRaises(ValidationError):
            coupon = Coupon(
                code='INVALID1',
                valid_from=self.now,
                valid_to=self.now + timedelta(days=30),
                discount=-1,
                active=True
            )
            coupon.full_clean()

        # Test discount above 100
        with self.assertRaises(ValidationError):
            coupon = Coupon(
                code='INVALID2',
                valid_from=self.now,
                valid_to=self.now + timedelta(days=30),
                discount=101,
                active=True
            )
            coupon.full_clean()

    def test_coupon_date_validation(self):
        """Test valid_from must be before valid_to"""
        with self.assertRaises(ValidationError):
            coupon = Coupon(
                code='INVALID3',
                valid_from=self.now + timedelta(days=30),  # Later date
                valid_to=self.now,  # Earlier date
                discount=25,
                active=True
            )
            coupon.full_clean()

    def test_coupon_is_valid(self):
        """Test coupon validity based on dates and active status"""
        # Test active coupon within valid dates
        self.assertTrue(self.coupon.active)
        self.assertLess(self.coupon.valid_from, timezone.now())
        self.assertGreater(self.coupon.valid_to, timezone.now())

        # Test expired coupon
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            valid_from=self.now - timedelta(days=60),
            valid_to=self.now - timedelta(days=30),
            discount=25,
            active=True
        )
        self.assertLess(expired_coupon.valid_to, timezone.now())

        # Test inactive coupon
        inactive_coupon = Coupon.objects.create(
            code='INACTIVE',
            valid_from=self.now,
            valid_to=self.now + timedelta(days=30),
            discount=25,
            active=False
        )
        self.assertFalse(inactive_coupon.active)

    def test_coupon_generate_instances(self):
        """Test the generate_instances class method"""
        initial_count = Coupon.objects.count()
        test_count = 5

        Coupon.generate_instances(test_count)

        # Check if the correct number of instances were created
        self.assertEqual(Coupon.objects.count(), initial_count + test_count)

        # Check if generated coupons have valid data
        for coupon in Coupon.objects.all():
            # Check code is not empty
            self.assertTrue(coupon.code)

            # Check discount is within valid range
            self.assertGreaterEqual(coupon.discount, 0)
            self.assertLessEqual(coupon.discount, 100)

            # Check dates are set
            self.assertIsNotNone(coupon.valid_from)
            self.assertIsNotNone(coupon.valid_to)

            # Check boolean field is set
            self.assertIsNotNone(coupon.active)


class CouponManagerTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()

        # Create active valid coupon
        self.valid_coupon = Coupon.objects.create(
            code='VALID',
            valid_from=self.now - timedelta(days=1),
            valid_to=self.now + timedelta(days=30),
            discount=25,
            active=True
        )

        # Create expired coupon
        self.expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            valid_from=self.now - timedelta(days=60),
            valid_to=self.now - timedelta(days=30),
            discount=25,
            active=True
        )

        # Create inactive coupon
        self.inactive_coupon = Coupon.objects.create(
            code='INACTIVE',
            valid_from=self.now,
            valid_to=self.now + timedelta(days=30),
            discount=25,
            active=False
        )

        # Create future coupon
        self.future_coupon = Coupon.objects.create(
            code='FUTURE',
            valid_from=self.now + timedelta(days=30),
            valid_to=self.now + timedelta(days=60),
            discount=25,
            active=True
        )

    def test_active_coupons(self):
        """Test filtering active and currently valid coupons"""
        active_coupons = Coupon.objects.filter(
            active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )

        # Should only include valid_coupon
        self.assertEqual(active_coupons.count(), 1)
        self.assertIn(self.valid_coupon, active_coupons)

        # Should not include expired, inactive, or future coupons
        self.assertNotIn(self.expired_coupon, active_coupons)
        self.assertNotIn(self.inactive_coupon, active_coupons)
        self.assertNotIn(self.future_coupon, active_coupons)