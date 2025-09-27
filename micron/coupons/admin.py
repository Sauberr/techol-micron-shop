from django.contrib import admin
from coupons.models.coupon import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "valid_from", "valid_to", "discount", "active", "created_at", "updated_at"]
    list_filter = ["active", "valid_from", "valid_to"]
    search_fields = ["code"]
    readonly_fields = ["created_at", "updated_at"]
