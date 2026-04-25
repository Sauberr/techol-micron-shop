from decimal import Decimal
from http import HTTPStatus
import requests

from django.utils.translation import gettext_lazy as _
import stripe
from django.http import HttpRequest, JsonResponse, HttpResponse

from common.views import TitleMixin
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic.base import TemplateView
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def select_payment(request: HttpRequest):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    context = {
        "order": order,
        "paypal_client_id": getattr(settings, "PAYPAL_CLIENT_ID", "test"),
    }
    return render(request, "payment/select_payment.html", context)


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
    else:
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
    else:
        return redirect("payment:select-payment")


def paypal_execute(request: HttpRequest):
    """Capture PayPal payment when user is redirected back."""
    token = request.GET.get('token')
    if not token:
        return redirect("payment:canceled")
        
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
        order_id = request.session.get("order_id", None)
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            order.paid = "paid"
            order.save()
        return redirect("payment:completed")
    
    return redirect("payment:canceled")


def liqpay_process(request: HttpRequest):
    """Process payment via LiqPay checkout."""
    from liqpay import LiqPay

    order_id = request.session.get("order_id", None)
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
    
    # We render an intermediate template that submits the form
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    
    context = {
        'data': data,
        'signature': signature
    }
    return render(request, "payment/liqpay_redirect.html", context)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def liqpay_callback(request: HttpRequest):
    """Webhook callback for LiqPay."""
    from liqpay import LiqPay

    data = request.POST.get('data')
    signature = request.POST.get('signature')
    
    if not data or not signature:
        return HttpResponse(status=400)
    
    public_key = getattr(settings, 'LIQPAY_PUBLIC_KEY', '')
    private_key = getattr(settings, 'LIQPAY_PRIVATE_KEY', '')
    
    liqpay = LiqPay(public_key, private_key)
    sign = liqpay.str_to_sign(private_key + data + private_key)
    
    if sign == signature:
        response = liqpay.decode_data_from_str(data)
        if response.get('status') in ['success', 'sandbox']:
            order_id = response.get('order_id')
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.paid = "paid"
                    order.save()
                    return HttpResponse(status=200)
                except Order.DoesNotExist:
                    pass
    
    return HttpResponse(status=400)


class SuccessTemplateView(TitleMixin, TemplateView):
    """Display payment success confirmation page."""

    template_name = "payment/completed.html"
    title = _("Payment Success")


class CanceledTemplateView(TitleMixin, TemplateView):
    """Display payment cancellation page."""

    template_name = "payment/canceled.html"
    title = _("Payment Canceled")
