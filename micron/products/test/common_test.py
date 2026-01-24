from abc import ABC
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from products.models.category import Category
from products.models.product import Product
from products.models.review import Review

User = get_user_model()


class BaseViewTestCase(ABC, TestCase):
    """Base test case for view tests"""
    path_name = None
    template_name = None
    title = None

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        if self.path_name:
            self.path = reverse(self.path_name)

    def test_view_url_exists(self):
        """Test that the view URL exists"""
        if self.path_name:
            response = self.client.get(reverse(self.path_name))
            self.assertIn(response.status_code, [200, 302, 301])

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        if self.path_name and self.template_name:
            response = self.client.get(reverse(self.path_name))
            if response.status_code == 200:
                self.assertTemplateUsed(response, self.template_name)


class BaseCategoryTestCase(ABC, TestCase):
    """Base test case for category-related tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )


class BaseProductTestCase(ABC, TestCase):
    """Base test case for product-related tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        self.test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            category=self.category,
            image=self.test_image,
            price=Decimal('99.99'),
            available=True,
            quantity=10
        )


class BaseReviewTestCase(ABC, TestCase):
    """Base test case for review-related tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        self.test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            category=self.category,
            image=self.test_image,
            price=Decimal('99.99'),
            available=True,
            quantity=10
        )

        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            stars=5,
            text='Great product!'
        )
