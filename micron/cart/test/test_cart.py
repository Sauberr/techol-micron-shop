from decimal import Decimal
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.urls import reverse

from cart.cart import Cart
from coupons.models import Coupon
from products.models.category import Category
from products.models.product import Product
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class MockSession(dict):
    """Mock session that behaves like a Django session"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modified = False


class CartTestCase(TestCase):
    """Tests for Cart functionality"""

    def setUp(self):
        self.factory = RequestFactory()
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        self.product1 = Product.objects.create(
            name='Product 1',
            slug='product-1',
            description='Test Product 1',
            category=self.category,
            image=self.test_image,
            price=Decimal('50.00'),
            bonus_points=Decimal('15.00'),
            available=True,
            quantity=10
        )

        self.product2 = Product.objects.create(
            name='Product 2',
            slug='product-2',
            description='Test Product 2',
            category=self.category,
            image=self.test_image,
            price=Decimal('75.00'),
            bonus_points=Decimal('22.50'),
            available=True,
            quantity=5
        )

    def test_cart_initialization(self):
        """Test cart initialization in session"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        self.assertIsNotNone(cart.cart)
        self.assertEqual(len(cart), 0)

    def test_add_product_to_cart(self):
        """Test adding a product to cart"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)

        self.assertEqual(len(cart), 2)
        self.assertIn(str(self.product1.id), cart.cart)

    def test_add_product_override_quantity(self):
        """Test overriding product quantity in cart"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        cart.add(self.product1, quantity=5, override_quantity=True)

        self.assertEqual(len(cart), 5)

    def test_remove_product_from_cart(self):
        """Test removing a product from cart"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        cart.remove(self.product1)

        self.assertEqual(len(cart), 0)
        self.assertNotIn(str(self.product1.id), cart.cart)

    def test_cart_total_price(self):
        """Test cart total price calculation"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)

        total = cart.get_total_price()
        self.assertEqual(total, 175)

    def test_cart_total_bonus_points(self):
        """Test cart total bonus points calculation"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)

        total_bonus = cart.get_total_bonus_points()
        # Use quantize to handle floating point precision
        self.assertEqual(total_bonus.quantize(Decimal('0.01')), Decimal('52.50'))

    def test_cart_with_coupon(self):
        """Test cart with coupon discount"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        # Create a coupon
        coupon = Coupon.objects.create(
            code='SAVE20',
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            discount=20,
            active=True
        )

        cart.add(self.product1, quantity=2)  # 100.00
        request.session['coupon_id'] = coupon.id
        cart = Cart(request)

        discount = cart.get_discount()
        self.assertEqual(discount, Decimal('20.00'))  # 20% of 100.00

    def test_cart_total_price_after_discount(self):
        """Test cart total price after discount"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        coupon = Coupon.objects.create(
            code='SAVE10',
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            discount=10,
            active=True
        )

        cart.add(self.product1, quantity=2)  # 100.00
        request.session['coupon_id'] = coupon.id
        cart = Cart(request)

        total = cart.get_total_price_after_discount()
        self.assertEqual(total, Decimal('90.00'))

    def test_cart_clear(self):
        """Test clearing the cart"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)
        cart.clear()

        self.assertEqual(len(cart), 0)

    def test_cart_iteration(self):
        """Test iterating over cart items"""
        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)

        items = list(cart)
        self.assertEqual(len(items), 2)

        for item in items:
            self.assertIn('product', item)
            self.assertIn('price', item)
            self.assertIn('quantity', item)
            self.assertIn('total_price', item)

    def test_cart_with_discount_price(self):
        """Test cart with product that has discount price"""
        product = Product.objects.create(
            name='Discounted Product',
            slug='discounted-product',
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('100.00'),
            price_with_discount=Decimal('80.00'),
            discount=True,
            available=True
        )

        request = self.factory.get('/')
        request.session = MockSession()
        cart = Cart(request)

        cart.add(product, quantity=1)

        items = list(cart)
        self.assertEqual(items[0]['price'], Decimal('80.00'))


class CartViewTestCase(TestCase):
    """Tests for Cart views"""

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

        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('99.99'),
            available=True,
            quantity=10
        )

    def test_cart_detail_view(self):
        """Test cart detail view"""
        response = self.client.get(reverse('cart:cart_summary'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'cart/cart-summary.html')

    def test_add_to_cart_view(self):
        """Test adding product to cart via view"""
        path = reverse('cart:cart_add', args=[self.product.id])
        data = {
            'quantity': 2,
            'override': False
        }

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_remove_from_cart_view(self):
        """Test removing product from cart via view"""
        # First add product
        add_path = reverse('cart:cart_add', args=[self.product.id])
        self.client.post(add_path, {'quantity': 1, 'override': False})

        # Then remove it
        remove_path = reverse('cart:cart_remove', args=[self.product.id])
        response = self.client.post(remove_path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_cart_persistence_across_requests(self):
        """Test that cart persists across requests"""

        # Add product to cart
        path = reverse('cart:cart_add', args=[self.product.id])
        self.client.post(path, {'quantity': 2, 'override': False})

        # Check cart detail
        response = self.client.get(reverse('cart:cart_summary'))
        self.assertContains(response, 'Test Product')
