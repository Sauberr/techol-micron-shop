from io import BytesIO

import weasyprint
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order


@shared_task
def send_order_invoice(order_id: int) -> None:
    order = Order.objects.get(id=order_id)
    subject = f"My Shop - Invoice no. {order.id}"
    message = "Please, find attached the invoice for your recent purchase."
    email = EmailMessage(subject, message, "admin@myshop.com", [order.email])
    html = render_to_string("orders/order/pdf.html", {"order": order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + "/css/pdf.css")]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    email.attach(f"order_{order.id}.pdf", out.getvalue(), "application/pdf")
    email.send()


@shared_task
def add_user_bonus_points(order_id: int) -> None:
    order = Order.objects.get(id=order_id)
    if order.paid == "paid" and order.user and order.bonus_points > 0:
        order.user.add_bonus_points(order.bonus_points)


@shared_task
def payment_completed(order_id: int) -> None:
    send_order_invoice.delay(order_id)
    add_user_bonus_points.delay(order_id)
