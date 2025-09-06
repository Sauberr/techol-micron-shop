from decimal import Decimal
from http import HTTPStatus

import stripe
from django.http import HttpRequest

from common.views import TitleMixin
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic.base import TemplateView
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request: HttpRequest):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))
        session_data = {
            "mode": "payment",
            "client_reference_id": order_id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        for item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal(100)),
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,
                        },
                    },
                    "quantity": item.quantity,
                }
            )
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code, percent_off=order.discount, duration="once"
            )
            session_data["discounts"] = [{"coupon": stripe_coupon.id}]
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=HTTPStatus.SEE_OTHER)
    else:
        return render(request, "payment/process.html", locals())


class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = "payment/completed.html"
    title = "Payment Success"


class CanceledTemplateView(TitleMixin, TemplateView):
    template_name = "payment/canceled.html"
    title = "Payment Canceled"
