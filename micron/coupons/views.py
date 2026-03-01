from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CouponApplyForm
from coupons.models.coupon import Coupon
from cart.cart import Cart


@require_POST
def coupon_apply(request):
    """Apply discount coupon to cart (supports AJAX)."""

    now = timezone.now()
    form = CouponApplyForm(request.POST)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                coupon = Coupon.objects.get(
                    code__iexact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True,
                )

                if not coupon.has_uses_left():
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "This coupon has reached its usage limit.",
                            "message_type": "error",
                        }
                    )

                request.session["coupon_id"] = coupon.id
                Coupon.objects.filter(pk=coupon.pk).update(used_count=F("used_count") + 1)

                cart = Cart(request)
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Coupon applied successfully",
                        "message_type": "success",
                        "coupon": {"code": coupon.code, "discount": coupon.discount},
                        "discount_amount": float(cart.get_discount()),
                        "subtotal": float(cart.get_total_price()),
                        "total_after_discount": float(
                            cart.get_total_price_after_discount()
                        ),
                    }
                )
            except Coupon.DoesNotExist:
                request.session["coupon_id"] = None
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Invalid coupon code",
                        "message_type": "error",
                    }
                )
        return JsonResponse({"success": False, "message": "Invalid form"})

    if form.is_valid():
        code = form.cleaned_data["code"]
        try:
            coupon = Coupon.objects.get(
                code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True
            )
            if coupon.has_uses_left():
                request.session["coupon_id"] = coupon.id
                Coupon.objects.filter(pk=coupon.pk).update(used_count=F("used_count") + 1)
            else:
                request.session["coupon_id"] = None
        except Coupon.DoesNotExist:
            request.session["coupon_id"] = None
    return redirect("cart:cart_summary")


@require_POST
def coupon_remove(request):
    """Remove applied coupon from cart (supports AJAX)."""

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if "coupon_id" in request.session:
            del request.session["coupon_id"]

        cart = Cart(request)
        total_price = cart.get_total_price()
        return JsonResponse(
            {
                "success": True,
                "message": "Coupon removed successfully.",
                "message_type": "success",
                "total_price": float(total_price),
                "subtotal": float(total_price),
                "discount": "0",
                "total_after_discount": float(total_price),
                "total_bonus_points": str(cart.get_total_bonus_points()),
            }
        )

    if "coupon_id" in request.session:
        del request.session["coupon_id"]
    return redirect("cart:cart_summary")
