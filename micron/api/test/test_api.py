from decimal import Decimal
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from orders.models import Order
from products.models.category import Category
from products.models.product import Product


User = get_user_model()

API_VERSION = 'v1'


def api_reverse(viewname, args=None, kwargs=None):
    """Helper function to reverse API URLs with version"""

    url = f'/en/api/{API_VERSION}/'

    if viewname.startswith('api:'):
        viewname = viewname.replace('api:', '')

    # Map view names to URL patterns
    url_patterns = {
        'token_obtain_pair': 'token/',
        'token_refresh': 'token/refresh/',
        'token_verify': 'token/verify/',
        'categories-list': 'categories/',
        'categories-detail': f'categories/{args[0]}/' if args else 'categories/',
        'products-list': 'products/',
        'products-detail': f'products/{args[0]}/' if args else 'products/',
        'orders-list': 'orders/',
        'orders-detail': f'orders/{args[0]}/' if args else 'orders/',
        'users-list': 'users/',
        'users-detail': f'users/{args[0]}/' if args else 'users/',
    }

    return url + url_patterns.get(viewname, viewname)


class APIAuthenticationTestCase(APITestCase):
    """Tests for API authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

    def test_obtain_jwt_token(self):
        """Test obtaining JWT token with valid credentials"""
        path = api_reverse('api:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Test obtaining token with invalid credentials"""
        path = api_reverse('api:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_refresh_jwt_token(self):
        """Test refreshing JWT token"""

        refresh = RefreshToken.for_user(self.user)

        path = api_reverse('api:token_refresh')
        data = {'refresh': str(refresh)}

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('access', response.data)

    def test_verify_jwt_token(self):
        """Test verifying JWT token"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        path = api_reverse('api:token_verify')
        data = {'token': access_token}

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class APICategoryTestCase(APITestCase):
    """Tests for Category API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_categories(self):
        """Test listing all categories"""
        path = api_reverse('api:categories-list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_category(self):
        """Test retrieving a specific category"""
        path = api_reverse('api:categories-detail', args=[self.category.id])
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['name'], 'Electronics')

    def test_create_category_as_admin(self):
        """Test creating category as admin user"""
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:categories-list')
        data = {
            'name': 'Books',
            'slug': 'books'
        }

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_category_as_regular_user(self):
        """Test that regular users cannot create categories"""
        path = api_reverse('api:categories-list')
        data = {
            'name': 'Books',
            'slug': 'books'
        }

        response = self.client.post(path, data)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_update_category_as_admin(self):
        """Test updating category as admin"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:categories-detail', args=[self.category.id])
        data = {
            'name': 'Updated Electronics',
            'slug': 'updated-electronics'
        }

        response = self.client.put(path, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Electronics')

    def test_delete_category_as_admin(self):
        """Test deleting category as admin"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:categories-detail', args=[self.category.id])
        response = self.client.delete(path)

        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)


class APIProductTestCase(APITestCase):
    """Tests for Product API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
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
            available=True
        )

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_products(self):
        """Test listing all products"""
        path = api_reverse('api:products-list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_product(self):
        """Test retrieving a specific product"""
        path = api_reverse('api:products-detail', args=[self.product.id])
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(Decimal(response.data['price']), Decimal('99.99'))

    def test_filter_products_by_category(self):
        """Test filtering products by category"""
        path = api_reverse('api:products-list')
        response = self.client.get(path, {'category': self.category.id})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        for product in response.data['results']:
            self.assertEqual(product['category'], self.category.id)

    def test_create_product_as_admin(self):
        """Test creating product as admin user"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:products-list')

        test_image = SimpleUploadedFile('new_test.jpg', b'fake image content', 'image/jpeg')

        data = {
            'name': 'New Product',
            'slug': 'new-product',
            'description': 'New Description',
            'category': self.category.id,
            'price': '149.99',
            'available': True,
            'quantity': 10,
            'image': test_image
        }

        response = self.client.post(path, data, format='multipart')

        self.assertNotEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_create_product_as_regular_user(self):
        """Test that regular users cannot create products"""
        path = api_reverse('api:products-list')
        data = {
            'name': 'New Product',
            'slug': 'new-product',
            'description': 'New Description',
            'category': self.category.id,
            'price': '149.99',
            'available': True
        }

        response = self.client.post(path, data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class APIOrderTestCase(APITestCase):
    """Tests for Order API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
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

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_user_orders(self):
        """Test listing user's own orders"""
        path = api_reverse('api:orders-list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_user_order(self):
        """Test retrieving user's own order"""
        path = api_reverse('api:orders-detail', args=[self.order.id])
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['first_name'], 'John')

    def test_user_cannot_see_other_orders(self):
        """Test that users can only see their own orders"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='other123'
        )

        other_order = Order.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            address='456 Test Ave',
            postal_code='67890',
            city='Test Town',
            user=other_user
        )

        path = api_reverse('api:orders-list')
        response = self.client.get(path)

        # Should only see own order
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.order.id)

    def test_admin_can_see_all_orders(self):
        """Test that admin can see all orders"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:orders-list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class APIUserTestCase(APITestCase):
    """Tests for User API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

    def test_list_users_as_admin(self):
        """Test listing users as admin"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:users-list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_list_users_as_regular_user(self):
        """Test that regular users cannot list users"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:users-list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_retrieve_own_user(self):
        """Test retrieving own user data"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        path = api_reverse('api:users-detail', args=[self.user.id])
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['username'], 'testuser')


class APIFilterTestCase(APITestCase):
    """Tests for API filtering functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category1 = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.category2 = Category.objects.create(
            name='Books',
            slug='books'
        )

        self.test_image = SimpleUploadedFile('test.jpg', b'', 'image/jpeg')

        Product.objects.create(
            name='Laptop',
            slug='laptop',
            description='Test',
            category=self.category1,
            image=self.test_image,
            price=Decimal('999.99'),
            available=True
        )

        Product.objects.create(
            name='Book 1',
            slug='book-1',
            description='Test',
            category=self.category2,
            image=self.test_image,
            price=Decimal('19.99'),
            available=True
        )

        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_filter_products_by_price_range(self):
        """Test filtering products by price range"""
        path = api_reverse('api:products-list')
        response = self.client.get(path, {'price_min': '50', 'price_max': '1000'})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        for product in response.data['results']:
            price = Decimal(product['price'])
            self.assertGreaterEqual(price, Decimal('50'))
            self.assertLessEqual(price, Decimal('1000'))

    def test_search_products_by_name(self):
        """Test searching products by name"""
        path = api_reverse('api:products-list')
        response = self.client.get(path, {'search': 'Laptop'})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        if len(response.data['results']) > 0:
            self.assertIn('Laptop', response.data['results'][0]['name'])
