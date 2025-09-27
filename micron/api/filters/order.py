from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model
from orders.models.order import Order
from coupons.models import Coupon

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

    email = filters.CharFilter(
        field_name="email",
        lookup_expr="icontains",
        label="Email",
        help_text="Search orders by customer email",
    )

    city = filters.CharFilter(
        field_name="city",
        lookup_expr="icontains",
        label="City",
        help_text="Search orders by city",
    )

    postal_code = filters.CharFilter(
        field_name="postal_code",
        lookup_expr="icontains",
        label="Postal Code",
        help_text="Search orders by postal code",
    )

    paid = filters.ChoiceFilter(
        field_name="paid",
        choices=[("paid", "Paid"), ("unpaid", "Unpaid")],
        label="Payment Status",
        help_text="Filter orders by payment status",
    )

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
            "first_name",
            "last_name",
            "email",
            "city",
            "postal_code",
            "paid",
            "user",
            "created_at",
            "has_coupon",
        ]
