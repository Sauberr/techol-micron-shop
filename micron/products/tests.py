from http import HTTPStatus
from django.urls import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os

from products.models import Category, Product, Review
from user_account.models import User


class BaseCategoryTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )


class CategoryModelTestCase(BaseCategoryTestCase):
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(str(self.category), 'Test Category')

    def test_category_absolute_url(self):
        expected_url = reverse('products:list_category', args=[self.category.slug])
        self.assertEqual(self.category.get_absolute_url(), expected_url)

    def test_category_generate_instances(self):
        Category.generate_instances(count=5)
        self.assertEqual(Category.objects.count(), 6)  # 5 new + 1 from setUp


class BaseProductTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # Create a test image
        img_path = os.path.join(settings.MEDIA_ROOT, 'test_image.jpg')
        with open(img_path, 'wb') as f:
            f.write(b'fake image data')

        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(img_path, 'rb').read(),
            content_type='image/jpeg'
        )

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            category=self.category,
            image=self.image,
            price=99.99,
            available=True
        )

    def tearDown(self):
        # Clean up the test image
        if self.product.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.product.image))
            if os.path.exists(image_path):
                os.remove(image_path)


class ProductModelTestCase(BaseProductTestCase):
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.slug, 'test-product')
        self.assertEqual(self.product.price, 99.99)
        self.assertTrue(self.product.available)
        self.assertFalse(self.product.discount)
        self.assertEqual(str(self.product), 'Test Product')

    def test_product_absolute_url(self):
        expected_url = reverse('products:product_detail', args=[self.product.slug])
        self.assertEqual(self.product.get_absolute_url(), expected_url)

    def test_product_with_discount(self):
        self.product.discount = True
        self.product.price_with_discount = 79.99
        self.product.save()

        self.assertTrue(self.product.discount)
        self.assertEqual(self.product.price_with_discount, 79.99)

    def test_product_generate_instances(self):
        initial_count = Product.objects.count()
        Product.generate_instances(count=5)
        self.assertEqual(Product.objects.count(), initial_count + 5)


class BaseReviewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            category=self.category,
            image='products/default.jpg',
            price=99.99
        )

        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            stars=5,
            text='Great product!'
        )


class ReviewModelTestCase(BaseReviewTestCase):
    def test_review_creation(self):
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.stars, 5)
        self.assertEqual(self.review.text, 'Great product!')
        self.assertEqual(str(self.review), str(self.user))

    def test_review_stars_choices(self):
        # Test that stars value is within valid choices
        valid_stars = [choice[0] for choice in Review.STARS_CHOICES]
        self.assertIn(self.review.stars, valid_stars)

    def test_review_generate_instances(self):
        initial_count = Review.objects.count()
        Review.generate_instances(count=5)
        self.assertEqual(Review.objects.count(), initial_count + 5)

    def test_review_invalid_stars(self):
        with self.assertRaises(Exception):
            Review.objects.create(
                user=self.user,
                product=self.product,
                stars=6,  # Invalid star value
                text='Invalid review'
            )


class ProductViewTestCase(BaseProductTestCase):
    def test_product_detail_view(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['product'], self.product)

    def test_product_list_view(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('products' in response.context)


class CategoryViewTestCase(BaseCategoryTestCase):
    def test_category_list_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('category' in response.context)