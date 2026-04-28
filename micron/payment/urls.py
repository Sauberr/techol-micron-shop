from django.urls import path
from payment.views import CanceledTemplateView, SuccessTemplateView, payment_process, select_payment, paypal_process, paypal_execute, LiqPayProcessView, LiqPayCallbackView

from . import webhooks

app_name: str = "payment"

urlpatterns = [
    path("process/", payment_process, name="process"),
    path("paypal-process/", paypal_process, name="paypal-process"),
    path("paypal-execute/", paypal_execute, name="paypal-execute"),
    path("liqpay-process/", LiqPayProcessView.as_view(), name="liqpay-process"),
    path("liqpay-callback/", LiqPayCallbackView.as_view(), name="liqpay-callback"),
    path("select/", select_payment, name="select-payment"),
    path("completed/", SuccessTemplateView.as_view(), name="completed"),
    path("canceled/", CanceledTemplateView.as_view(), name="canceled"),
    path("webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
]
