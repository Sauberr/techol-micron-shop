from coupons.forms import CouponApplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from products.models import Product

from .cart import Cart
from .forms import CartAddProductForm


def cart_summary(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
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
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
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
