from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from products.models.category import Category
from products.models.product import Product
from products.models.product_image import ProductImage
from products.models.review import Review


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ["name", "slug"]
    readonly_fields = ["created_at", "updated_at"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
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
    ]
    list_filter = ["available", "created_at", "updated_at"]
    list_editable = ["price", "available"]
    list_display_links = ("name", "thumbnail", "slug")
    inlines = [ProductImageInline]
    readonly_fields = ["created_at", "updated_at"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "stars", "text", "created_at")
    fields = ("user", "product", "stars", "text",)
    readonly_fields = ("created_at", "updated_at")


