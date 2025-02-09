from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin

from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ["name", "slug"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


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
        "available",
        "discount",
        "created",
        "updated",
    ]
    list_filter = ["available", "created", "updated"]
    list_editable = ["price", "available"]
    list_display_links = ("name", "thumbnail", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "stars", "text", "created_at")
    fields = ("user", "product", "stars", "text", "created_at")