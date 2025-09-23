from django.contrib.auth import get_user_model

from rest_framework import serializers
from products.models.category import Category
from products.models.product import Product
from api.serializers.review import ReviewSerializer

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=Category.objects.all()
    )
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_reviews(self, obj):
        reviews = obj.review_set.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data
