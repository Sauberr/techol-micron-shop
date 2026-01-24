from http import HTTPStatus
from unittest.mock import Mock, patch
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models.category import Category
from products.models.product import Product

User = get_user_model()


class PaymentViewTestCase(TestCase):
    """Tests for payment views"""

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

    def test_payment_process_view_get(self):
        """Test payment process GET request"""
        session = self.client.session
        session['order_id'] = self.order.id
        session.save()

        path = reverse('payment:process')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'payment/process.html')

    @patch('stripe.checkout.Session.create')
    def test_payment_process_view_post(self, mock_stripe_session):
        """Test payment process POST request with Stripe"""
        # Mock Stripe session
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test'
        mock_stripe_session.return_value = mock_session

        session = self.client.session
        session['order_id'] = self.order.id
        session.save()

        path = reverse('payment:process')
        response = self.client.post(path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, 'https://checkout.stripe.com/test')

    @patch('stripe.checkout.Session.create')
    @patch('stripe.Coupon.create')
    def test_payment_process_with_coupon(self, mock_coupon, mock_stripe_session):
        """Test payment process with coupon discount"""
        from coupons.models import Coupon
        from django.utils import timezone
        from datetime import timedelta

        # Create coupon
        coupon = Coupon.objects.create(
            code='SAVE20',
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
            discount=20,
            active=True
        )

        self.order.coupon = coupon
        self.order.discount = 20
        self.order.save()

        # Mock Stripe responses
        mock_stripe_coupon = Mock()
        mock_stripe_coupon.id = 'stripe_coupon_id'
        mock_coupon.return_value = mock_stripe_coupon

        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test'
        mock_stripe_session.return_value = mock_session

        session = self.client.session
        session['order_id'] = self.order.id
        session.save()

        path = reverse('payment:process')
        response = self.client.post(path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_coupon.assert_called_once()

    def test_payment_success_view(self):
        """Test payment success page"""
        path = reverse('payment:completed')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'payment/completed.html')

    def test_payment_canceled_view(self):
        """Test payment canceled page"""
        path = reverse('payment:canceled')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'payment/canceled.html')

    def test_payment_process_without_order(self):
        """Test payment process without order in session"""
        path = reverse('payment:process')
        response = self.client.get(path)

        # Should return 404 when no order_id in session
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class PaymentIntegrationTestCase(TestCase):
    """Integration tests for payment flow"""

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

    def test_complete_payment_flow(self):
        """Test complete flow from cart to payment"""
        self.client.login(username='testuser', password='testpass123')

        # Add product to cart
        cart_path = reverse('cart:cart_add', args=[self.product.id])
        self.client.post(cart_path, {'quantity': 1, 'override': False})

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

        # Access payment process
        payment_path = reverse('payment:process')
        response = self.client.get(payment_path)

        self.assertEqual(response.status_code, HTTPStatus.OK)


class StripeWebhookTestCase(TestCase):
    """Tests for Stripe webhook handling"""

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
            user=self.user,
            stripe_id='pi_test123'
        )

    @patch('payment.webhooks.payment_completed.delay')
    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_success(self, mock_construct_event, mock_payment_task):
        """Test webhook handling for successful payment"""
        # Mock Stripe event with proper object structure
        mock_session = Mock()
        mock_session.mode = 'payment'
        mock_session.payment_status = 'paid'
        mock_session.client_reference_id = str(self.order.id)
        mock_session.payment_intent = 'pi_test123'

        mock_data = Mock()
        mock_data.object = mock_session

        mock_event = Mock()
        mock_event.type = 'checkout.session.completed'
        mock_event.data = mock_data

        mock_construct_event.return_value = mock_event

        path = reverse('payment:stripe-webhook')
        response = self.client.post(
            path,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        # Verify webhook processed successfully
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid, 'paid')
        self.assertEqual(self.order.stripe_id, 'pi_test123')
