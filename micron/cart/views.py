from coupons.forms import CouponApplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from products.models import Product
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .cart import Cart
from .forms import CartAddProductForm


def cart_summary(request):
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
def cart_add(request, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if product.quantity == 0:
        messages.error(request, _("Product is out of stock"))
        return redirect(product.get_absolute_url())

    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd["quantity"]

        if quantity > product.quantity:
            messages.error(request, _("Not enough stock available"))
            return redirect(product.get_absolute_url())

        cart.add(
            product=product,
            quantity=cd["quantity"],
            override_quantity=cd["override"]
        )
    return redirect("cart:cart_summary")


@require_POST
def cart_remove(request, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_summary")


@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart:cart_summary")
