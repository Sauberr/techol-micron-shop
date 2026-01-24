from django.contrib.auth import get_user_model

from orders.models import Order
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

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
    """API endpoint for CRUD operations on product categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    filterset_class = CategoryFilter

    def get_queryset(self):
        qs = Category.objects.all()
        if self.request.query_params.get('show_deleted') == 'true' and self.request.user.is_staff:
            qs = Category.all_objects.all()
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def undelete(self, request, pk=None):
        category = Category.all_objects.get(pk=pk)
        if category.deleted:
            category.undelete()
            serializer = self.get_serializer(category)
            return Response({'status': 'restored', 'data': serializer.data})
        return Response({'status': 'not deleted', 'message': 'Category is not deleted'})


class ProductModelViewSet(ModelViewSet):
    """API endpoint for CRUD operations on products."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    filterset_class = ProductFilter
    ordering_fields = ["translations__name", "created_at"]

    def get_queryset(self):
        qs = Product.objects.all()
        if self.request.query_params.get('show_deleted') == 'true' and self.request.user.is_staff:
            qs = Product.all_objects.all()
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def undelete(self, request, pk=None):
        product = Product.all_objects.get(pk=pk)
        if product.deleted:
            product.undelete()
            serializer = self.get_serializer(product)
            return Response({'status': 'restored', 'data': serializer.data})
        return Response({'status': 'not deleted', 'message': 'Product is not deleted'})


class UserModelViewSet(ModelViewSet):
    """API endpoint for CRUD operations on users."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    ordering_fields = ["username"]
    filterset_class = UserFilter

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        List action requires admin, other actions use IsAdminOrReadOnly
        """
        if self.action == 'list':
            return [IsAdminUser()]
        return [IsAdminOrReadOnly(), IsAuthenticated()]

    def get_queryset(self):
        qs = get_user_model().objects.all()
        if self.request.query_params.get('show_deleted') == 'true' and self.request.user.is_staff:
            qs = get_user_model().all_objects.all()
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def undelete(self, request, pk=None):
        user = get_user_model().all_objects.get(pk=pk)
        if user.deleted:
            user.undelete()
            serializer = self.get_serializer(user)
            return Response({'status': 'restored', 'data': serializer.data})
        return Response({'status': 'not deleted', 'message': 'User is not deleted'})


class OrderModelViewSet(ModelViewSet):
    """API endpoint for CRUD operations on orders."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated)
    ordering_fields = ["username", "created_at", "first_name", "last_name", "email"]
    filterset_class = OrderFilter

    def get_queryset(self):
        """
        Regular users can only see their own orders.
        Admins can see all orders.
        """
        qs = Order.objects.all()

        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)

        if self.request.query_params.get('show_deleted') == 'true' and self.request.user.is_staff:
            qs = Order.all_objects.all()
            if not self.request.user.is_staff:
                qs = qs.filter(user=self.request.user)

        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def undelete(self, request, pk=None):
        order = Order.all_objects.get(pk=pk)
        if order.deleted:
            order.undelete()
            serializer = self.get_serializer(order)
            return Response({'status': 'restored', 'data': serializer.data})
        return Response({'status': 'not deleted', 'message': 'Order is not deleted'})
