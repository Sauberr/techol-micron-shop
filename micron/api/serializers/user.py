from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    favorite_products = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_verified_email",
            "image",
            "bonus_points",
            "favorite_products",
            "date_joined",
            "last_login",
        )
        read_only_fields = ("id", "date_joined", "last_login")
