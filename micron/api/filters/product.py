from django_filters.rest_framework import FilterSet, filters

from products.models.product import Product
from products.models.category import Category
from taggit.models import Tag


class ProductFilter(FilterSet):
    name = filters.CharFilter(
        field_name="translations__name",
        lookup_expr="icontains",
        label="Product Name",
        help_text="Search products by name",
    )
    price = filters.RangeFilter(
        field_name="price",
        label="Price Range",
        help_text="Filter products within a price range",
    )
    available = filters.BooleanFilter(
        field_name="available",
        label="Available",
        help_text="Filter products by availability",
    )
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name="category",
        label="Category",
        help_text="Filter products by category",
    )
    discount = filters.BooleanFilter(
        field_name="discount",
        label="Discounted",
        help_text="Filter products on discount",
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags",
        label="Tags",
        help_text="Select multiple tags to filter products",
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "price",
            "available",
            "category",
            "discount",
            "tags",
        ]

