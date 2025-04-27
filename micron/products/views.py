import logging

from cart.forms import CartAddProductForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Case, DecimalField, F, Max, Min, When
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Category, Product, Review
from taggit.models import Tag

from django.utils.translation import gettext_lazy as _
from .forms import ReviewForm
from .recommender import Recommender
from .utils import paginateprodcuts, searchproducts

logger = logging.getLogger("main")


def index(request):
    products, search_query = searchproducts(request)
    reviews = Review.objects.all()
    context = {
        "title": "| Products",
        "products": products,
        "search_query": search_query,
        "reviews": reviews,
    }
    return render(request, "index.html", context)


def products(request):
    logger.info("products")
    products, search_query = searchproducts(request)

    discount = request.GET.get("discount")
    order = request.GET.get("order")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if discount in ["true", "false"]:
        products = products.filter(discount=(discount == "true"))

    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            products = products.annotate(
                effective_price=Case(
                    When(
                        discount=True,
                        price_with_discount__isnull=False,
                        then=F('price_with_discount')
                    ),
                    default=F('price'),
                    output_field=DecimalField()
                )
            ).filter(
                effective_price__gte=min_price,
                effective_price__lte=max_price
            )
        except (ValueError, TypeError):
            pass

    order_fields = {
        "price": "price",
        "-price": "-price",
        "date": "created",
        "-date": "-created",
    }

    if order in order_fields:
        if 'price' in order_fields[order]:
            products = products.annotate(
                effective_price=Case(
                    When(
                        discount=True,
                        price_with_discount__isnull=False,
                        then=F('price_with_discount')
                    ),
                    default=F('price'),
                    output_field=DecimalField()
                )
            )

            if order == '-price':
                products = products.order_by('-effective_price')
            else:
                products = products.order_by('effective_price')
        else:
            products = products.order_by(order_fields[order])

    price_range = products.aggregate(
        min_price=Min(
            Case(
                When(
                    discount=True,
                    price_with_discount__isnull=False,
                    then='price_with_discount'
                ),
                default='price',
                output_field=DecimalField()
            )
        ),
        max_price=Max(
            Case(
                When(
                    discount=True,
                    price_with_discount__isnull=False,
                    then='price_with_discount'
                ),
                default='price',
                output_field=DecimalField()
            )
        )
    )

    custom_range, products = paginateprodcuts(request, products, 6)
    context = {
        "title": "| Products",
        "products": products,
        "search_query": search_query,
        "custom_range": custom_range,
        "min_price": float(price_range['min_price'] or 0),
        "max_price": float(price_range['max_price'] or 1000),
        "selected_min_price": min_price or price_range['min_price'] or 0,
        "selected_max_price": max_price or price_range['max_price'] or 1000,
    }
    return render(request, "products/products.html", context)


def product_detail(request, product_slug: str):
    language = request.LANGUAGE_CODE
    try:
        product = Product.objects.get(
            translations__language_code=language,
            translations__slug=product_slug,
            available=True,
        )
    except Product.DoesNotExist:
        product_in_other_language = get_object_or_404(
            Product,
            translations__slug=product_slug,
            available=True,
        )
        product_slug_in_current_language = product_in_other_language.translations.filter(
            language_code=language).first().slug
        product = get_object_or_404(
            Product,
            translations__language_code=language,
            translations__slug=product_slug_in_current_language,
            available=True,
        )

    cart_product_form = CartAddProductForm(product=product)

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    reviews = Review.objects.filter(product=product)
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


def tag_list(request, tag_slug=None):
    products = Product.objects.all().order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {"products": products, "tag": tag, "title": "| Tags"}

    return render(request, "products/tag_list.html", context)


def list_category(request, category_slug=None):
    if category_slug:
        language = request.LANGUAGE_CODE
        category = get_object_or_404(
            Category,
            translations__slug=category_slug,
        )
        category_slug_in_new_language = category.translations.filter(language_code=language).first().slug
        category = get_object_or_404(
            Category,
            translations__language_code=language,
            translations__slug=category_slug_in_new_language,
        )
        products = Product.objects.filter(category=category)
        context = {"products": products, "category": category}
    return render(request, "products/list_category.html", context)


@login_required
def add_to_favorite(request, product_id: int):
    try:
        product = Product.objects.get(pk=product_id)
        request.user.favorite_products.add(product)
    except Product.DoesNotExist:
        pass
    return redirect("products:products")


@login_required
def favorite_products(request):
    if request.user.is_authenticated:
        favorite_products = request.user.favorite_products.all()
        context = {
            "favorite_products": favorite_products,
            "title": "| Favorite products",
        }
        return render(request, "products/favorite_products.html", context)
    else:
        return redirect("user_account:login")


@login_required
def delete_from_favorites(request, product_id: int):
    try:
        product = Product.objects.get(pk=product_id)
        request.user.favorite_products.remove(product)
    except Product.DoesNotExist:
        pass
    return redirect("products:favorite_products")


@login_required
def add_review(request, product_id: int):
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
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        messages.error(request, "You do not have permission to delete this review")
        return redirect("products:product_detail", product_slug=review.product.slug)

    review.delete()
    messages.success(request, "Review deleted successfully")
    return redirect("products:product_detail", product_slug=review.product.slug)


@login_required
def update_review(request, review_id: int):
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
