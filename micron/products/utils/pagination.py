from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, Page
from django.http import HttpRequest
from products.models.product import Product


def paginate_products(request: HttpRequest, products: Product, results) -> tuple[range, Page]:
    """Paginate products queryset."""

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