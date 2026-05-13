from django.db.models import Case, DecimalField, F, Max, Min, QuerySet, When

from products.models.product import Product
from products.models.category import Category


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

    result = Product.objects.filter(available=True).aggregate(
        min_price=Min(get_effective_price_expr()),
        max_price=Max(get_effective_price_expr())
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


def filter_by_category(queryset: QuerySet, category_slug: str, language_code: str) -> QuerySet:
    """Filter products by category slug and language."""

    if not category_slug:
        return queryset

    try:
        category = Category.objects.get(
            translations__slug=category_slug,
            translations__language_code=language_code,
        )
        return queryset.filter(category=category)
    except (Category.DoesNotExist, Category.MultipleObjectsReturned):
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
        "date": "created_at",
        "-date": "-created_at",
    }

    if order not in order_map:
        return queryset

    if order in ["price", "-price"] and "effective_price" not in queryset.query.annotations:
        queryset = queryset.annotate(effective_price=get_effective_price_expr())

    return queryset.order_by(order_map[order])


def get_user_favorite_ids(user) -> set:
    """Get set of favorite product IDs for user."""

    if user.is_authenticated:
        return set(user.favorite_products.values_list('id', flat=True))
    return set()
