from django.http import HttpRequest, JsonResponse

from coupons.forms import CouponApplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from products.models import Product
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from http import HTTPStatus

from .cart import Cart
from .forms import CartAddProductForm


def cart_summary(request: HttpRequest):
    """Display shopping cart with items, quantities and coupon form."""

    cart = Cart(request)
    cart_updated = False

    for item in cart:
        product = item["product"]
        quantity = item["quantity"]

        if not hasattr(product, "quantity"):
            continue

        if not product.available or product.quantity == 0:
            cart.remove(product)
            messages.warning(request, _(
                "'{0}' has been removed from your cart as it is no longer available."
            ).format(product.name))
            cart_updated = True

        elif product.quantity < quantity:
            cart.add(product=product, quantity=product.quantity, override_quantity=True)
            messages.warning(request, _(
                "Quantity for '{0}' has been adjusted to {1} due to limited stock."
            ).format(product.name, product.quantity))
            cart_updated = True

    for item in cart:

        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True},
            product=item["product"],
        )
    coupon_apply_form = CouponApplyForm()
    context = {
        "title": "| Your shopping cart",
        "cart": cart,
        "coupon_apply_form": coupon_apply_form,
    }
    return render(request, "cart/cart-summary.html", context)


@require_POST
def cart_add(request: HttpRequest, product_id: int):
    """Add product to cart with stock validation (supports AJAX)."""

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if product.quantity == 0:
        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": str(_("Product is out of stock")),
                    "message_type": "error",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        messages.error(request, _("Product is out of stock"))
        return redirect(product.get_absolute_url())

    form = CartAddProductForm(request.POST)
    if not form.is_valid():
        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": str(_("Invalid form data")),
                    "message_type": "error",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        messages.error(request, _("Invalid form data"))
        return redirect(product.get_absolute_url())

    quantity = form.cleaned_data["quantity"]
    if quantity > product.quantity:
        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": str(_("Not enough stock available")),
                    "message_type": "error",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        messages.error(request, _("Not enough stock available"))
        return redirect(product.get_absolute_url())

    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=form.cleaned_data["override"],
    )

    if is_ajax:
        response_data = {
            "success": True,
            "message": str(_("Cart updated successfully")),
            "message_type": "success",
            "cart_total": len(cart),
            "subtotal": str(cart.get_total_price()),
            "total_bonus_points": str(cart.get_total_bonus_points()),
            "total_after_discount": str(cart.get_total_price_after_discount()),
        }
        if cart.coupon:
            response_data["discount"] = str(cart.get_discount())
        return JsonResponse(response_data)

    messages.success(request, _("Product added to cart successfully"))
    return redirect(product.get_absolute_url())


@require_POST
def cart_remove(request: HttpRequest, product_id: int):
    """Remove product from cart (supports AJAX)."""

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    cart.remove(product)

    if is_ajax:
        response_data = {
            "success": True,
            "message": str(_("Product removed from cart successfully")),
            "message_type": "success",
            "cart_total": len(cart),
            "subtotal": str(cart.get_total_price()),
            "total_bonus_points": str(cart.get_total_bonus_points()),
            "total_after_discount": str(cart.get_total_price_after_discount()),
        }
        if cart.coupon:
            response_data["discount"] = str(cart.get_discount())
        return JsonResponse(response_data)
    messages.success(request, _("Product removed from cart successfully"))

    return redirect("cart:cart_summary")


@require_POST
def cart_clear(request: HttpRequest):
    """Remove all items from cart (supports AJAX)."""

    cart = Cart(request)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if is_ajax:
        cart.clear()
        return JsonResponse(
            {
                "success": True,
                "message": str(_("Cart cleared successfully")),
                "message_type": "success",
                "cart_total": 0,
            }
        )

    messages.success(request, _("Cart cleared successfully"))

    cart.clear()
    return redirect("cart:cart_summary")
