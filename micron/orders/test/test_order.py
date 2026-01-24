from decimal import Decimal
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from coupons.models import Coupon
from orders.models import Order, OrderItem
from products.models.category import Category
from products.models.product import Product

User = get_user_model()


class OrderModelTestCase(TestCase):
    """Tests for Order model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Test Street',
            postal_code='12345',
            city='Test City',
            user=self.user
        )

    def test_order_creation(self):
        """Test order creation with valid data"""
        self.assertEqual(self.order.first_name, 'John')
        self.assertEqual(self.order.last_name, 'Doe')
        self.assertEqual(self.order.email, 'john@example.com')
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.paid, 'unpaid')

    def test_order_string_representation(self):
        """Test order string representation"""
        self.assertEqual(str(self.order), f'Order {self.order.id}')

    def test_order_total_cost_calculation(self):
        """Test order total cost calculation"""
        category = Category.objects.create(name='Test', slug='test')
        test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test',
            category=category,
            image=test_image,
            price=Decimal('50.00'),
            available=True
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            price=Decimal('50.00'),
            quantity=2
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            price=Decimal('50.00'),
            quantity=1
        )

        total = self.order.get_total_cost_before_discount()
        self.assertEqual(total, Decimal('150.00'))

    def test_order_discount_calculation(self):
        """Test order discount calculation"""
        category = Category.objects.create(name='Test', slug='test')
        test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test',
            category=category,
            image=test_image,
            price=Decimal('100.00'),
            available=True
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            price=Decimal('100.00'),
            quantity=1
        )

        self.order.discount = 20
        self.order.save()

        discount = self.order.get_discount()
        self.assertEqual(discount, Decimal('20.00'))

    def test_order_total_cost_with_discount(self):
        """Test order total cost with discount"""
        category = Category.objects.create(name='Test', slug='test')
        test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test',
            category=category,
            image=test_image,
            price=Decimal('100.00'),
            available=True
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            price=Decimal('100.00'),
            quantity=1
        )

        self.order.discount = 10
        self.order.save()

        total = self.order.get_total_cost()
        self.assertEqual(total, Decimal('90.00'))

    def test_order_with_coupon(self):
        """Test order with coupon"""
        coupon = Coupon.objects.create(
            code='SAVE20',
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            discount=20,
            active=True
        )

        self.order.coupon = coupon
        self.order.discount = coupon.discount
        self.order.save()

        self.assertEqual(self.order.coupon, coupon)
        self.assertEqual(self.order.discount, 20)

    def test_order_stripe_url_generation(self):
        """Test Stripe URL generation for order"""
        self.order.stripe_id = 'pi_test123456'
        self.order.save()

        stripe_url = self.order.get_stripe_url()
        self.assertIn('dashboard.stripe.com', stripe_url)
        self.assertIn('pi_test123456', stripe_url)

    def test_order_timestamps(self):
        """Test that order has timestamps"""
        self.assertIsNotNone(self.order.created_at)
        self.assertIsNotNone(self.order.updated_at)

    def test_order_user_set_null_on_delete(self):
        """Test that order user remains when user is soft deleted"""
        order_id = self.order.id
        user_id = self.user.id
        self.user.delete()

        order = Order.objects.get(id=order_id)

        self.assertIsNotNone(order.user)
        self.assertEqual(order.user.id, user_id)

        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertTrue(User.all_objects.filter(id=user_id).exists())

    def test_order_ordering(self):
        """Test order default ordering"""
        order2 = Order.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            address='456 Test Ave',
            postal_code='67890',
            city='Test Town',
            user=self.user
        )

        orders = Order.objects.all()
        self.assertEqual(orders[0].id, order2.id)


class OrderItemModelTestCase(TestCase):
    """Tests for OrderItem model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Test Street',
            postal_code='12345',
            city='Test City',
            user=self.user
        )

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('75.00'),
            available=True
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal('75.00'),
            quantity=2,
            user=self.user
        )

    def test_order_item_creation(self):
        """Test order item creation"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.price, Decimal('75.00'))
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_item_cost_calculation(self):
        """Test order item cost calculation"""
        cost = self.order_item.get_cost()
        self.assertEqual(cost, Decimal('150.00'))

    def test_order_item_string_representation(self):
        """Test order item string representation"""
        self.assertEqual(str(self.order_item), str(self.order_item.id))

    def test_order_item_soft_delete(self):
        """Test soft delete functionality for order items"""
        item_id = self.order_item.id
        self.order_item.delete()

        # Should not be in regular queryset
        self.assertFalse(OrderItem.objects.filter(id=item_id).exists())

        # But should be in all_objects queryset
        self.assertTrue(OrderItem.all_objects.filter(id=item_id).exists())

    def test_order_item_cascade_delete(self):
        """Test that order items remain when order is soft deleted"""
        order_id = self.order.id
        item_id = self.order_item.id
        self.order.delete()

        self.assertEqual(OrderItem.objects.filter(id=item_id).count(), 1)

        self.assertFalse(Order.objects.filter(id=order_id).exists())
        self.assertTrue(Order.all_objects.filter(id=order_id).exists())


class OrderViewTestCase(TestCase):
    """Tests for Order views"""

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
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('99.99'),
            available=True,
            quantity=10
        )

        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Test Street',
            postal_code='12345',
            city='Test City',
            user=self.user
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal('99.99'),
            quantity=1,
            user=self.user
        )

    def test_order_create_view_authenticated(self):
        """Test order creation view when authenticated"""
        self.client.login(username='testuser', password='testpass123')

        # First add product to cart
        cart_path = reverse('cart:cart_add', args=[self.product.id])
        self.client.post(cart_path, {'quantity': 1, 'override': False})

        # Then create order
        path = reverse('orders:order_create')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': '123 Street',
            'postal_code': '12345',
            'city': 'City'
        }

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_order_create_view_unauthenticated(self):
        """Test order creation view when not authenticated"""
        path = reverse('orders:order_create')
        response = self.client.get(path)

        # Should redirect to login (view requires authentication)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn('login', response.url)

    def test_orders_list_view_authenticated(self):
        """Test orders list view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')

        path = reverse('orders:orders')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Order')

    def test_orders_list_view_unauthenticated(self):
        """Test orders list view redirects when not authenticated"""
        path = reverse('orders:orders')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_order_detail_view(self):
        """Test order detail view"""
        self.client.login(username='testuser', password='testpass123')

        path = reverse('orders:detail_order', args=[self.order.id])
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Test Product')

    def test_delete_order_view(self):
        """Test deleting an order"""
        self.client.login(username='testuser', password='testpass123')

        order_id = self.order.id
        path = reverse('orders:delete_order', args=[order_id])
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Order.objects.filter(id=order_id).exists())


class OrderIntegrationTestCase(TestCase):
    """Integration tests for order flow"""

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

        self.product1 = Product.objects.create(
            name='Product 1',
            slug='product-1',
            description='Test',
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
            description='Test',
            category=self.category,
            image=self.test_image,
            price=Decimal('75.00'),
            bonus_points=Decimal('22.50'),
            available=True,
            quantity=5
        )

    def test_complete_order_flow(self):
        """Test complete order flow from cart to order creation"""
        self.client.login(username='testuser', password='testpass123')

        # Add products to cart
        cart_path1 = reverse('cart:cart_add', args=[self.product1.id])
        self.client.post(cart_path1, {'quantity': 2, 'override': False})

        cart_path2 = reverse('cart:cart_add', args=[self.product2.id])
        self.client.post(cart_path2, {'quantity': 1, 'override': False})

        # Create order
        order_path = reverse('orders:order_create')
        order_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Test Street',
            'postal_code': '12345',
            'city': 'Test City'
        }

        response = self.client.post(order_path, order_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Verify order was created
        order = Order.objects.latest('created_at')
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.user, self.user)

        # Verify order items were created
        self.assertEqual(order.items.count(), 2)

    def test_order_with_coupon_flow(self):
        """Test order flow with coupon discount"""
        self.client.login(username='testuser', password='testpass123')

        # Create coupon
        coupon = Coupon.objects.create(
            code='SAVE20',
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            discount=20,
            active=True
        )

        # Add product to cart
        cart_path = reverse('cart:cart_add', args=[self.product1.id])
        self.client.post(cart_path, {'quantity': 2, 'override': False})

        # Apply coupon
        coupon_path = reverse('coupons:apply')
        self.client.post(coupon_path, {'code': 'SAVE20'})

        # Create order
        order_path = reverse('orders:order_create')
        order_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'address': '456 Test Ave',
            'postal_code': '67890',
            'city': 'Test Town'
        }

        response = self.client.post(order_path, order_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Verify order has coupon applied
        order = Order.objects.latest('created_at')
        self.assertEqual(order.coupon, coupon)
        self.assertEqual(order.discount, 20)
