from rest_framework import serializers

from api.serializers.order_item import OrderItemSerializer
from orders.models.order import Order


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_items(self, obj):
        items = obj.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return serializer.data
