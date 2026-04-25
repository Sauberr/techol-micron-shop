from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model
from orders.models.order import Order, STATUS

User = get_user_model()


class OrderFilter(FilterSet):
    first_name = filters.CharFilter(
        field_name="first_name",
        lookup_expr="icontains",
        label="First Name",
        help_text="Search orders by customer first name",
    )

    last_name = filters.CharFilter(
        field_name="last_name",
        lookup_expr="icontains",
        label="Last Name",
        help_text="Search orders by customer last name",
    )

    email = filters.CharFilter(field_name="email", lookup_expr="icontains")

    region = filters.CharFilter(
        field_name="region",
        lookup_expr="icontains"
    )
    city = filters.CharFilter(
        field_name="city",
        lookup_expr="icontains"
    )
    post_office = filters.CharFilter(
        field_name="post_office",
        lookup_expr="icontains"
    )

    paid = filters.ChoiceFilter(field_name="paid", choices=STATUS)

    user = filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        field_name="user",
        label="User",
        help_text="Filter orders by user",
    )

    created_at = filters.DateFromToRangeFilter(
        field_name="created_at",
        label="Created Date Range",
        help_text="Filter orders by creation date range",
    )

    has_coupon = filters.BooleanFilter(
        field_name="coupon",
        lookup_expr="isnull",
        exclude=True,
        label="Has Coupon",
        help_text="Filter orders that have a coupon applied",
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "region",
            "city",
            "post_office",
            "paid",
            "discount",
            "created_at",
            "updated_at",
        ]
