from django.contrib.auth import get_user_model

from orders.models import Order
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from products.models.category import Category
from products.models.product import Product
from api.serializers.product import ProductSerializer
from api.serializers.category import CategorySerializer
from api.serializers.order import OrderSerializer
from .filters.category import CategoryFilter
from .filters.order import OrderFilter
from .filters.product import ProductFilter
from .filters.user import UserFilter

from .permissions import IsAdminOrReadOnly
from .serializers.user import UserSerializer


class CategoryModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    filterset_class = CategoryFilter


class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    filterset_class = ProductFilter
    ordering_fields = ["translations__name", "created_at"]


class UserModelViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    ordering_fields = ["username"]
    filterset_class = UserFilter


class OrderModelViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    ordering_fields = ["username", "created_at", "first_name", "last_name", "email"]
    filterset_class = OrderFilter
