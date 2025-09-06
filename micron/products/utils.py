from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, Page
from django.db.models import Q
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import Product


def searchproducts(request: HttpRequest) -> tuple[Product, str]:
    search_query = ""
    if request.GET.get("search_query"):
        search_query = request.GET["search_query"]

    products = Product.objects.distinct().filter(
        Q(translations__name__icontains=search_query)
    )

    if not products.exists():
        messages.error(request, _("No search results found. Please try again."))

    return products, search_query


def paginateprodcuts(request: HttpRequest, products: Product, results) -> tuple[range, Page]:
    page = request.GET.get("page")
    paginator = Paginator(products, results)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        products = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        products = paginator.page(page)
    leftindex = int(page) - 4
    if leftindex < 1:
        leftindex = 1
    rightindex = int(page) + 5
    if rightindex > paginator.num_pages:
        rightindex = paginator.num_pages + 1
    custom_range = range(leftindex, rightindex)
    return custom_range, products
