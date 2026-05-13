import base64
import hashlib
import json
from decimal import Decimal
from http import HTTPStatus

import requests
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from liqpay import LiqPay

from common.views import TitleMixin
from orders.models import Order
from orders.tasks import send_telegram_order_paid
from .tasks import payment_completed

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


@login_required
def select_payment(request: HttpRequest):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    context = {
        "order": order,
        "paypal_client_id": getattr(settings, "PAYPAL_CLIENT_ID", "test"),
    }
    return render(request, "payment/select_payment.html", context)


@login_required
def payment_process(request: HttpRequest):
    """Process payment via Stripe checkout session."""

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
    return render(request, "payment/process.html", {"order": order})


def get_paypal_access_token():
    client_id = getattr(settings, "PAYPAL_CLIENT_ID", "")
    secret_key = getattr(settings, "PAYPAL_SECRET_KEY", "")
    base_url = "https://api-m.sandbox.paypal.com" if settings.DEBUG else "https://api-m.paypal.com"
    url = f"{base_url}/v1/oauth2/token"
    data = {"grant_type": "client_credentials"}
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    response = requests.post(url, auth=(client_id, secret_key), headers=headers, data=data)
    if response.ok:
        return response.json()['access_token']
    return None

@login_required
def paypal_process(request: HttpRequest):
    """Process payment via PayPal checkout session."""
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        access_token = get_paypal_access_token()
        if not access_token:
            return redirect("payment:canceled")
            
        base_url = "https://api-m.sandbox.paypal.com" if settings.DEBUG else "https://api-m.paypal.com"
        url = f"{base_url}/v2/checkout/orders"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        return_url = request.build_absolute_uri(reverse("payment:paypal-execute"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))
        
        total_cost = order.get_total_cost()

        data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": str(order.id),
                "amount": {
                    "currency_code": "USD",
                    "value": f"{total_cost:.2f}"
                }
            }],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "user_action": "PAY_NOW"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.ok:
            order_data = response.json()
            for link in order_data.get('links', []):
                if link['rel'] == 'approve':
                    return redirect(link['href'])
        
        return redirect("payment:canceled")
    return redirect("payment:select-payment")


@login_required
def paypal_execute(request: HttpRequest):
    """Capture PayPal payment when user is redirected back."""
    token = request.GET.get('token')
    order_id = request.session.get("order_id")

    if not token or not order_id:
        return redirect("payment:canceled")

    order = get_object_or_404(Order, id=order_id)

    access_token = get_paypal_access_token()
    if not access_token:
        return redirect("payment:canceled")

    base_url = "https://api-m.sandbox.paypal.com" if settings.DEBUG else "https://api-m.paypal.com"
    url = f"{base_url}/v2/checkout/orders/{token}/capture"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers)
    if response.ok:
        order.paid = "paid"
        order.save()
        payment_completed.delay(order.id)
        send_telegram_order_paid.delay(order.id)
        return redirect("payment:completed")

    return redirect("payment:canceled")


@method_decorator(login_required, name='dispatch')
class LiqPayProcessView(View):
    """Process payment via LiqPay checkout."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        order_id = request.session.get("order_id", None)
        if not order_id:
            return redirect("payment:canceled")

        order = get_object_or_404(Order, id=order_id)

        public_key = getattr(settings, 'LIQPAY_PUBLIC_KEY', '')
        private_key = getattr(settings, 'LIQPAY_PRIVATE_KEY', '')

        if not public_key or not private_key:
            return redirect("payment:canceled")

        liqpay = LiqPay(public_key, private_key)

        total_cost = order.get_total_cost()
        result_url = request.build_absolute_uri(reverse("payment:completed"))
        server_url = request.build_absolute_uri(reverse("payment:liqpay-callback"))

        params = {
            'action': 'pay',
            'amount': str(total_cost),
            'currency': 'USD',
            'description': f'Order {order.id}',
            'order_id': str(order.id),
            'version': '3',
            'sandbox': 1 if settings.DEBUG else 0,
            'result_url': result_url,
            'server_url': server_url,
        }

        form_html = liqpay.cnb_form(params)

        context = {
            'order': order,
            'form_html': form_html
        }
        return render(request, "payment/liqpay_checkout.html", context)


@method_decorator(csrf_exempt, name='dispatch')
class LiqPayCallbackView(View):
    """Webhook callback for LiqPay."""

    def post(self, request, *args, **kwargs):
        data = request.POST.get('data')
        signature = request.POST.get('signature')

        if not data or not signature:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        private_key = getattr(settings, 'LIQPAY_PRIVATE_KEY', '')
        sign_str = private_key + data + private_key
        sign = base64.b64encode(hashlib.sha1(sign_str.encode('utf-8')).digest()).decode('utf-8')

        if sign != signature:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        decoded_data = base64.b64decode(data).decode('utf-8')
        response = json.loads(decoded_data)

        try:
            order = Order.objects.get(id=response['order_id'])
        except Order.DoesNotExist:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        if response.get('status') == 'success':
            order.paid = "paid"
            order.save()
            payment_completed.delay(order.id)
            send_telegram_order_paid.delay(order.id)
        elif response.get('status') in ['sandbox', 'wait_accept', 'processing', 'wait_secure']:
            if response.get('status') == 'sandbox':
                order.paid = "paid"
                order.save()
                payment_completed.delay(order.id)
                send_telegram_order_paid.delay(order.id)

        return HttpResponse()


class SuccessTemplateView(TitleMixin, TemplateView):
    """Display payment success confirmation page."""

    template_name = "payment/completed.html"
    title = _("Payment Success")


class CanceledTemplateView(TitleMixin, TemplateView):
    """Display payment cancellation page."""

    template_name = "payment/canceled.html"
    title = _("Payment Canceled")
