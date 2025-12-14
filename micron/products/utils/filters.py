from django.db.models import Case, DecimalField, F, Max, Min, QuerySet, When

from products.models.product import Product


def get_effective_price_expr():
    """Returns Case expression for effective price (with discount if applicable)."""

    return Case(
        When(
            discount=True,
            price_with_discount__isnull=False,
            then=F('price_with_discount')
        ),
        default=F('price'),
        output_field=DecimalField()
    )


def get_price_range() -> dict:
    """Get min and max prices from all available products."""

    effective_price = Case(
        When(
            discount=True,
            price_with_discount__isnull=False,
            then='price_with_discount'
        ),
        default='price',
        output_field=DecimalField()
    )

    result = Product.objects.filter(available=True).aggregate(
        min_price=Min(effective_price),
        max_price=Max(effective_price)
    )

    return {
        'min_price': float(result['min_price'] or 0),
        'max_price': float(result['max_price'] or 1000),
    }


def filter_by_discount(queryset: QuerySet, discount: str) -> QuerySet:
    """Filter products by discount status."""

    if discount in ["true", "false"]:
        return queryset.filter(discount=(discount == "true"))
    return queryset


def filter_by_price_range(queryset: QuerySet, min_price: str, max_price: str) -> QuerySet:
    """Filter products by price range."""

    if not (min_price and max_price):
        return queryset

    try:
        min_val = float(min_price)
        max_val = float(max_price)
        return queryset.annotate(
            effective_price=get_effective_price_expr()
        ).filter(
            effective_price__gte=min_val,
            effective_price__lte=max_val
        )
    except (ValueError, TypeError):
        return queryset


def apply_ordering(queryset: QuerySet, order: str) -> QuerySet:
    """Apply ordering to products queryset."""

    order_map = {
        "price": "effective_price",
        "-price": "-effective_price",
        "date": "created",
        "-date": "-created",
    }

    if order not in order_map:
        return queryset

    if order in ["price", "-price"]:
        queryset = queryset.annotate(effective_price=get_effective_price_expr())

    return queryset.order_by(order_map[order])


def get_user_favorite_ids(user) -> set:
    """Get set of favorite product IDs for user."""

    if user.is_authenticated:
        return set(user.favorite_products.values_list('id', flat=True))
    return set()
