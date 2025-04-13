from django.urls import path
from payment.views import CanceledTemplateView, SuccessTemplateView, payment_process

from . import webhooks

app_name: str = "payment"

urlpatterns = [
    path("process/", payment_process, name="process"),
    path("completed/", SuccessTemplateView.as_view(), name="completed"),
    path("canceled/", CanceledTemplateView.as_view(), name="canceled"),
    path("webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
]
