from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from products.models.product import Product


def search_products(request: HttpRequest) -> tuple[Product, str]:
    """Search products by name containing the search query."""

    search_query = ""
    if request.GET.get("search_query"):
        search_query = request.GET["search_query"]

    products = Product.objects.distinct().filter(
        Q(translations__name__icontains=search_query)
    )

    if not products.exists():
        messages.error(request, _("No search results found. Please try again."))

    return products, search_query