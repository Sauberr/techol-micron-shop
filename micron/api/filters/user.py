from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters



class UserFilter(FilterSet):
    username = filters.CharFilter(field_name="username", lookup_expr="icontains", label="Username",
                                  help_text="Search users by username")
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains", label="First Name",
                                    help_text="Search users by first name")
    last_name = filters.CharFilter(
        field_name="last_name",
        lookup_expr="icontains",
        label="Last Name",
        help_text="Search users by last name",
    )
    email = filters.CharFilter(field_name="email", lookup_expr="icontains", label="Email",
                                    help_text="Search users by email")
    is_verified_email = filters.BooleanFilter(
        field_name="is_verified_email",
        label="Verified Email",
        help_text="Filter users by email verification status",
    )
    is_super_user = filters.BooleanFilter(
        field_name="is_superuser",
        label="Super User",
        help_text="Filter users by superuser status",
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_verified_email",
            "is_super_user",
        ]

