from django.contrib.auth import get_user_model

from rest_framework import serializers
from products.models.review import Review


User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Review
        fields = "__all__"
