from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter, highlight_deleted
from products.models.category import Category
from products.models.product import Product
from products.models.product_image import ProductImage
from products.models.review import Review


@admin.register(Category)
class CategoryAdmin(SafeDeleteAdmin, TranslatableAdmin):
    """Category Admin"""
    list_display = ["name", "slug", "deleted", highlight_deleted]
    list_filter = (SafeDeleteAdminFilter,)
    readonly_fields = ["created_at", "updated_at"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return ProductImage.all_objects.filter(product=self.instance) if hasattr(self, 'instance') else qs


@admin.register(Product)
class ProductAdmin(SafeDeleteAdmin, TranslatableAdmin):
    """Product Admin"""

    def thumbnail(self, object):
        return format_html('<img src="{}" width="40";" />'.format(object.image.url))

    thumbnail.short_description = "Image"
    list_display = [
        "name",
        "slug",
        "thumbnail",
        "price",
        "quantity",
        "available",
        "discount",
        "created_at",
        "updated_at",
        "deleted",
        highlight_deleted,
    ]
    list_filter = ["available", "created_at", "updated_at", SafeDeleteAdminFilter]
    list_editable = ["price", "available"]
    list_display_links = ("name", "thumbnail", "slug")
    inlines = [ProductImageInline]
    readonly_fields = ["created_at", "updated_at"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(ProductImage)
class ProductImageAdmin(SafeDeleteAdmin):
    """ProductImage"""
    list_display = ("product", "image", "deleted")
    list_filter = (SafeDeleteAdminFilter,)


@admin.register(Review)
class ReviewAdmin(SafeDeleteAdmin):
    """Review Admin"""
    list_display = ("user", "product", "stars", "text", "created_at", "deleted")
    list_filter = (SafeDeleteAdminFilter,)
    list_select_related = ['user', 'product']
    fields = ("user", "product", "stars", "text")
    readonly_fields = ("created_at", "updated_at")


