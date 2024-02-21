from orders.models import Order
from orders.serializers import OrderSerializer
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAdminOrReadOnly


class CategoryModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)


class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["translations__name", "available"]
    ordering_fields = ["translations__name", "created"]


class OrderModelViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
