from django.contrib.auth import get_user_model
from parler_rest.serializers import TranslatableModelSerializer

from rest_framework import serializers
from products.models.category import Category
from products.models.product import Product
from api.serializers.review import ReviewSerializer

User = get_user_model()


class ProductSerializer(TranslatableModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField(
        required=True,
    )
    description = serializers.CharField(
        required=True,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_reviews(self, obj):
        reviews = obj.review_set.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data
