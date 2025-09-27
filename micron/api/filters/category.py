from django_filters.rest_framework import FilterSet, filters

from products.models.category import Category


class CategoryFilter(FilterSet):
    name = filters.CharFilter(
        field_name="translations__name",
        lookup_expr="icontains",
        label="Category Name",
        help_text="Search categories by name",
    )

    class Meta:
        model = Category
        fields = [
            "name",
        ]

