import stripe
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from http import HTTPStatus

from .tasks import payment_completed


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)

    if event.type == "checkout.session.completed":
        session = event.data.object
        if session.mode == "payment" and session.payment_status == "paid":
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=HTTPStatus.BAD_REQUEST)
            order.paid = "paid"
            order.stripe_id = session.payment_intent
            order.save()
            payment_completed.delay(order.id)

    return HttpResponse(status=HTTPStatus.OK)
