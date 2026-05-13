from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CouponApplyForm
from coupons.models.coupon import Coupon
from cart.cart import Cart


def _get_valid_coupon(code: str, now) -> Coupon | None:
    try:
        return Coupon.objects.get(
            code__iexact=code,
            valid_from__lte=now,
            valid_to__gte=now,
            active=True,
        )
    except (Coupon.DoesNotExist, Coupon.MultipleObjectsReturned):
        return None


@require_POST
def coupon_apply(request):
    """Apply discount coupon to cart (supports AJAX)."""

    now = timezone.now()
    form = CouponApplyForm(request.POST)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not form.is_valid():
        if is_ajax:
            return JsonResponse({"success": False, "message": "Invalid form"})
        return redirect("cart:cart_summary")

    code = form.cleaned_data["code"]
    coupon = _get_valid_coupon(code, now)

    if coupon is None:
        request.session["coupon_id"] = None
        if is_ajax:
            return JsonResponse({
                "success": False,
                "message": "Invalid coupon code",
                "message_type": "error",
            })
        return redirect("cart:cart_summary")

    if not coupon.has_uses_left():
        request.session["coupon_id"] = None
        if is_ajax:
            return JsonResponse({
                "success": False,
                "message": "This coupon has reached its usage limit.",
                "message_type": "error",
            })
        return redirect("cart:cart_summary")

    request.session["coupon_id"] = coupon.id

    if is_ajax:
        cart = Cart(request)
        return JsonResponse({
            "success": True,
            "message": "Coupon applied successfully",
            "message_type": "success",
            "coupon": {"code": coupon.code, "discount": coupon.discount},
            "discount_amount": float(cart.get_discount()),
            "subtotal": float(cart.get_total_price()),
            "total_after_discount": float(cart.get_total_price_after_discount()),
        })

    return redirect("cart:cart_summary")


@require_POST
def coupon_remove(request):
    """Remove applied coupon from cart (supports AJAX)."""

    if "coupon_id" in request.session:
        del request.session["coupon_id"]

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        cart = Cart(request)
        total_price = cart.get_total_price()
        return JsonResponse({
            "success": True,
            "message": "Coupon removed successfully.",
            "message_type": "success",
            "total_price": float(total_price),
            "subtotal": float(total_price),
            "discount": "0",
            "total_after_discount": float(total_price),
            "total_bonus_points": str(cart.get_total_bonus_points()),
        })

    return redirect("cart:cart_summary")