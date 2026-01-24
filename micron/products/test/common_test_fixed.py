from abc import ABC
from decimal import Decimal
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from products.models.category import Category
from products.models.product import Product
from products.models.product_image import ProductImage
from products.models.review import Review

User = get_user_model()


class BaseViewTestCase(ABC, TestCase):
    """Base test case for view testing"""
    path_name = None
    template_name = None
    title = None

    def setUp(self):
        self.path = reverse(self.path_name) if self.path_name is not None else None

    def test_get(self):
        if self.path is not None:
            response = self.client.get(self.path)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.context['title'], self.title)
            self.assertTemplateUsed(response, self.template_name)


class BaseProductTestCase(TestCase):
    """Base test case for product-related tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # Create test image
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

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


class BaseCategoryTestCase(TestCase):
    """Base test case for category-related tests"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )


class BaseReviewTestCase(TestCase):
    """Base test case for review-related tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            category=self.category,
            image=self.test_image,
            price=Decimal('99.99')
        )

        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            stars=5,
            text='Great product!'
        )
