from rest_framework import serializers
from coupons.models.coupon import Coupon


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = ("id", "code", "valid_from", "valid_to", "discount", "active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_code(self, value):
        instance = self.instance

        query = Coupon.objects.filter(code=value)

        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            raise serializers.ValidationError("Coupon with this code already exists.")

        return value

    def validate(self, data):
        if 'valid_from' in data and 'valid_to' in data:
            if data['valid_to'] <= data['valid_from']:
                raise serializers.ValidationError({
                    'valid_to': "The 'valid_to' date must be after the 'valid_from' date."
                })
        return data
