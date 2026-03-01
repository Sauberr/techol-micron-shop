from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter, highlight_deleted
from coupons.models.coupon import Coupon


@admin.register(Coupon)
class CouponAdmin(SafeDeleteAdmin):
    """Coupon Admin with SafeDelete support"""
    list_display = ["code", "valid_from", "valid_to", "discount", "active", "max_uses", "used_count", "created_at", "updated_at", "deleted", highlight_deleted]
    list_filter = ["active", "valid_from", "valid_to", SafeDeleteAdminFilter]
    search_fields = ["code"]
    readonly_fields = ["used_count", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)
