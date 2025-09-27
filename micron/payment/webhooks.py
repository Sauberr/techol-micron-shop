import stripe
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from http import HTTPStatus
from django.db import transaction

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
                with transaction.atomic():
                    try:
                        order = Order.objects.get(
                            id=session.client_reference_id
                        )
                    except Order.DoesNotExist:
                        return HttpResponse(status=HTTPStatus.BAD_REQUEST)

                    if order.paid == "paid":
                        return HttpResponse(status=HTTPStatus.OK)

                    order.paid = "paid"
                    order.stripe_id = session.payment_intent
                    order.save()

                    transaction.on_commit(lambda: payment_completed.delay(order.id))

            except Order.DoesNotExist:
                return HttpResponse(status=HTTPStatus.BAD_REQUEST)
            except Exception:
                return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return HttpResponse(status=HTTPStatus.OK)
