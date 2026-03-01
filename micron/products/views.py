from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from http import HTTPStatus
import logging

from cart.forms import CartAddProductForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from products.models.product import Product
from products.models.review import Review
from taggit.models import Tag

from django.utils.translation import gettext_lazy as _
from .forms import ReviewForm
from .recommender import Recommender
from .utils.filters import (
    apply_ordering,
    filter_by_category,
    filter_by_discount,
    filter_by_price_range,
    get_price_range,
    get_user_favorite_ids,
)
from .utils.pagination import paginate_products
from .utils.search import search_products

logger = logging.getLogger(__name__)


def index(request: HttpRequest):
    """Render homepage with featured products and reviews."""

    products, search_query = search_products(request)
    reviews = Review.objects.all().select_related("user", "product")
    context = {
        "title": "| Products",
        "products": products,
        "search_query": search_query,
        "reviews": reviews,
    }
    return render(request, "index.html", context)


def products(request: HttpRequest):
    """Display product listing with filters, sorting and pagination."""

    logger.info("products")

    try:
        discount = request.GET.get("discount")
        order = request.GET.get("order")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        category_slug = request.GET.get("category")

        products_qs, search_query = search_products(request)

        products_qs = filter_by_category(products_qs, category_slug, request.LANGUAGE_CODE)
        products_qs = filter_by_discount(products_qs, discount)
        products_qs = filter_by_price_range(products_qs, min_price, max_price)
        products_qs = apply_ordering(products_qs, order)

        custom_range, products_qs = paginate_products(request, products_qs, 5)
        favorite_ids = get_user_favorite_ids(request.user)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render(request, "products/ajax/products_list.html", {
                "products": products_qs,
                "custom_range": custom_range,
                "favorite_ids": favorite_ids,
            }).content.decode('utf-8')
            return JsonResponse({"success": True, "html": html})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": str(e)}, status=HTTPStatus.BAD_REQUEST)
        raise

    price_range = get_price_range()
    context = {
        "title": "| Products",
        "products": products_qs,
        "search_query": search_query,
        "custom_range": custom_range,
        "favorite_ids": favorite_ids,
        **price_range,
    }
    return render(request, "products/products.html", context)


def product_detail(request: HttpRequest, product_slug: str):
    """Display single product details with reviews and recommendations."""

    language = request.LANGUAGE_CODE
    try:
        product = Product.objects.get(
            translations__language_code=language,
            translations__slug=product_slug,
            available=True,
        )
    except Product.DoesNotExist:
        try:
            product_in_other_language = Product.objects.get(
                translations__slug=product_slug,
                available=True,
            )
            translation_in_current_language = product_in_other_language.translations.filter(
                language_code=language
            ).first()

            if not translation_in_current_language:
                raise Product.DoesNotExist(f"Product with slug '{product_slug}' has no translation in '{language}'")
            product = product_in_other_language
        except Product.DoesNotExist:
            raise Product.DoesNotExist(f"Product with slug '{product_slug}' not found")

    cart_product_form = CartAddProductForm(product=product)

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    reviews = Review.objects.filter(product=product).select_related("user")
    if reviews:
        average_stars = reviews.aggregate(Avg("stars"))["stars__avg"]
    else:
        average_stars = None
    context = {
        "product": product,
        "title": "| Product detail page",
        "cart_product_form": cart_product_form,
        "recommended_products": recommended_products,
        "reviews": reviews,
        "average_stars": average_stars,
    }
    return render(request, "products/single_product.html", context)


def tag_list(request: HttpRequest, tag_slug=None):
    """Filter and display products by tag."""

    products = Product.objects.all().order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {"products": products, "tag": tag, "title": "| Tags"}

    return render(request, "products/tag_list.html", context)


@login_required
@require_POST
def add_to_favorite(request: HttpRequest, product_id: int):
    """Add product to user favorites via AJAX."""

    try:
        product = Product.objects.get(pk=product_id)

        if request.user.favorite_products.filter(pk=product_id).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": f"{product.name} is already in favorites!",
                    "message_type": "info",
                    "already_favorited": True,
                }
            )

        request.user.favorite_products.add(product)
        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} added to favorites!",
                "message_type": "success",
            }
        )

    except Product.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Product not found",
            "message_type": "error",
        })


@login_required
def favorite_products(request: HttpRequest):
    """Display list of user favorite products."""

    if request.user.is_authenticated:
        favorite_products = request.user.favorite_products.all().prefetch_related("tags").select_related("category")
        context = {
            "favorite_products": favorite_products,
            "title": "| Favorite products",
        }
        return render(request, "products/favorite_products.html", context)
    else:
        return redirect("user_account:login")


@login_required
def delete_from_favorites(request: HttpRequest, product_id: int):
    """Remove product from user favorites."""

    try:
        product = Product.objects.get(pk=product_id)
        request.user.favorite_products.remove(product)
    except Product.DoesNotExist:
        pass
    return redirect("products:favorite_products")


@login_required
def add_review(request: HttpRequest, product_id: int):
    """Create new product review (one per user per product)."""

    product = get_object_or_404(Product, id=product_id)

    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.error(request, "You have already reviewed this product")
        return redirect("products:product_detail", product_slug=product.slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect("products:product_detail", product_slug=product.slug)
    else:
        form = ReviewForm()
    return render(
        request,
        "products/add_reviews.html",
        {"title": "| Add review", "form": form, "product": product},
    )


@login_required
def delete_review(request: HttpRequest, review_id: int):
    """Delete user's own product review."""

    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        messages.error(request, "You do not have permission to delete this review")
        return redirect("products:product_detail", product_slug=review.product.slug)

    review.delete()
    messages.success(request, "Review deleted successfully")
    return redirect("products:product_detail", product_slug=review.product.slug)


@login_required
def update_review(request: HttpRequest, review_id: int):
    """Update user's own product review."""

    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        messages.error(request, _("You do not have permission to update this review"))
        return redirect("products:product_detail", product_slug=review.product.slug)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _("Review updated successfully"))
            return redirect("products:product_detail", product_slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "products/update_review.html",
        {"title": "| Update review", "form": form, "product": review.product},
    )
