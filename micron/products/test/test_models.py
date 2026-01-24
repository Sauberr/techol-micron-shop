from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.urls import reverse
from safedelete.models import HARD_DELETE

from products.models.category import Category
from products.models.product import Product
from products.models.product_image import ProductImage
from products.models.review import Review
from products.test.common_test import (
    BaseCategoryTestCase,
    BaseProductTestCase,
    BaseReviewTestCase
)

User = get_user_model()


class CategoryModelTestCase(BaseCategoryTestCase):
    """Tests for Category model"""

    def test_category_creation(self):
        """Test category creation with valid data"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')
        self.assertEqual(str(self.category), 'Electronics')

    def test_category_absolute_url(self):
        """Test category absolute URL generation"""
        expected_url = reverse('products:list_category', args=[self.category.slug])
        self.assertEqual(self.category.get_absolute_url(), expected_url)

    def test_category_unique_slug_validation(self):
        """Test that duplicate category slugs are allowed (translatable field)"""

        duplicate_category = Category.objects.create(
            name='Duplicate',
            slug='electronics'
        )
        # Should succeed without raising an error
        self.assertIsNotNone(duplicate_category.id)

    def test_category_soft_delete(self):
        """Test soft delete functionality for categories"""
        category_id = self.category.id
        self.category.delete()

        # Category should not be in regular queryset
        self.assertFalse(Category.objects.filter(id=category_id).exists())

        # But should be in all_objects queryset
        self.assertTrue(Category.all_objects.filter(id=category_id).exists())

    def test_category_generate_instances(self):
        """Test category generation helper method"""
        initial_count = Category.objects.count()
        Category.generate_instances(count=3)
        self.assertEqual(Category.objects.count(), initial_count + 3)

    def test_category_string_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), self.category.name)


class ProductModelTestCase(BaseProductTestCase):
    """Tests for Product model"""

    def test_product_creation(self):
        """Test product creation with valid data"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.slug, 'test-product')
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.category, self.category)
        self.assertTrue(self.product.available)

    def test_product_string_representation(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), 'Test Product')

    def test_product_absolute_url(self):
        """Test product absolute URL generation"""
        expected_url = reverse('products:product_detail', args=[self.product.slug])
        self.assertEqual(self.product.get_absolute_url(), expected_url)

    def test_product_bonus_points_calculation(self):
        """Test automatic bonus points calculation on save"""
        product = Product.objects.create(
            name='Bonus Test',
            slug='bonus-test',
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('100.00')
        )
        # Use quantize to handle floating point precision
        self.assertEqual(product.bonus_points.quantize(Decimal('0.01')), Decimal('30.00'))

    def test_product_bonus_points_with_discount(self):
        """Test bonus points calculation with discount price"""
        product = Product.objects.create(
            name='Discount Test',
            slug='discount-test',
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('100.00'),
            price_with_discount=Decimal('80.00'),
            discount=True
        )
        # Use quantize to handle floating point precision
        self.assertEqual(product.bonus_points.quantize(Decimal('0.01')), Decimal('24.00'))

    def test_product_price_validation(self):
        """Test product price minimum validation"""
        with self.assertRaises(ValidationError):
            product = Product(
                name='Invalid Price',
                slug='invalid-price',
                description='Test',
                category=self.category,
                image=self.test_image,
                price=Decimal('0.00')
            )
            product.full_clean()

    def test_product_quantity_default(self):
        """Test product quantity default value"""
        product = Product.objects.create(
            name='Quantity Test',
            slug='quantity-test',
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('50.00')
        )
        self.assertEqual(product.quantity, 0)

    def test_product_available_default(self):
        """Test product available default value"""
        self.assertTrue(self.product.available)

    def test_product_discount_default(self):
        """Test product discount default value"""
        self.assertFalse(self.product.discount)

    def test_product_tags(self):
        """Test product tags functionality"""
        self.product.tags.add('electronics', 'sale')
        self.assertEqual(self.product.tags.count(), 2)
        self.assertIn('electronics', [tag.name for tag in self.product.tags.all()])

    def test_product_generate_instances(self):
        """Test product generation helper method"""
        initial_count = Product.objects.count()
        Product.generate_instances(count=3)
        self.assertEqual(Product.objects.count(), initial_count + 3)


class ProductImageModelTestCase(BaseProductTestCase):
    """Tests for ProductImage model"""

    def test_product_image_creation(self):
        """Test product image creation"""
        image = SimpleUploadedFile(
            name='additional_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        product_image = ProductImage.objects.create(
            product=self.product,
            image=image
        )

        self.assertEqual(product_image.product, self.product)
        self.assertIsNotNone(product_image.image)

    def test_product_image_string_representation(self):
        """Test product image string representation"""
        image = SimpleUploadedFile(
            name='test_additional.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        product_image = ProductImage.objects.create(
            product=self.product,
            image=image
        )

        expected_str = f"Image for {self.product.name}"
        self.assertEqual(str(product_image), expected_str)

    def test_product_image_relationship(self):
        """Test product image relationship with product"""
        image1 = SimpleUploadedFile('img1.jpg', b'', 'image/jpeg')
        image2 = SimpleUploadedFile('img2.jpg', b'', 'image/jpeg')

        ProductImage.objects.create(product=self.product, image=image1)
        ProductImage.objects.create(product=self.product, image=image2)

        self.assertEqual(self.product.additional_images.count(), 2)

    def test_product_image_cascade_delete(self):
        """Test that product images remain when product is soft deleted"""
        image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')
        product_image = ProductImage.objects.create(product=self.product, image=image)

        product_id = self.product.id
        image_id = product_image.id

        self.product.delete()

        self.assertEqual(
            ProductImage.objects.filter(id=image_id).count(), 1
        )

        # Product is soft deleted
        self.assertFalse(Product.objects.filter(id=product_id).exists())
        self.assertTrue(Product.all_objects.filter(id=product_id).exists())

    def test_product_image_soft_delete(self):
        """Test soft delete functionality for product images"""
        image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')
        product_image = ProductImage.objects.create(
            product=self.product,
            image=image
        )

        image_id = product_image.id
        product_image.delete()

        # Should not be in regular queryset
        self.assertFalse(ProductImage.objects.filter(id=image_id).exists())

        # But should be in all_objects queryset
        self.assertTrue(ProductImage.all_objects.filter(id=image_id).exists())


class ReviewModelTestCase(BaseReviewTestCase):
    """Tests for Review model"""

    def test_review_creation(self):
        """Test review creation with valid data"""
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.stars, 5)
        self.assertEqual(self.review.text, 'Great product!')

    def test_review_string_representation(self):
        """Test review string representation"""
        self.assertEqual(str(self.review), str(self.user))

    def test_review_stars_choices(self):
        """Test review stars choices (1-5)"""
        for stars in range(1, 6):
            review = Review.objects.create(
                user=self.user,
                product=self.product,
                stars=stars,
                text=f'Review with {stars} stars'
            )
            self.assertEqual(review.stars, stars)

    def test_review_user_soft_delete(self):
        """Test that review remains intact when user is soft deleted"""
        review_id = self.review.id
        user_id = self.user.id

        self.user.delete()

        review = Review.objects.get(id=review_id)
        self.assertIsNotNone(review.user)
        self.assertEqual(review.user.id, user_id)

        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertTrue(User.all_objects.filter(id=user_id).exists())

    def test_review_product_soft_delete(self):
        """Test that review remains intact when product is soft deleted"""
        review_id = self.review.id
        product_id = self.product.id
        # Soft delete the product
        self.product.delete()

        # Review should still exist and reference the product
        review = Review.objects.get(id=review_id)
        self.assertIsNotNone(review.product)
        self.assertEqual(review.product.id, product_id)

        # Product should be soft deleted (not in regular queryset but in all_objects)
        self.assertFalse(Product.objects.filter(id=product_id).exists())
        self.assertTrue(Product.all_objects.filter(id=product_id).exists())

    def test_review_generate_instances(self):
        """Test review generation helper method"""
        initial_count = Review.objects.count()
        Review.generate_instances(count=3)
        self.assertEqual(Review.objects.count(), initial_count + 3)

    def test_multiple_reviews_per_product(self):
        """Test that a product can have multiple reviews"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

        Review.objects.create(
            user=user2,
            product=self.product,
            stars=4,
            text='Good product'
        )

        self.assertEqual(self.product.review_set.count(), 2)

    def test_review_timestamps(self):
        """Test that review has created_at and updated_at timestamps"""
        self.assertIsNotNone(self.review.created_at)
        self.assertIsNotNone(self.review.updated_at)
