from io import BytesIO

import weasyprint
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order


@shared_task
def send_order_invoice(order_id: int):
    """
    Task to send an e-mail invoice when an order is paid.
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f"My Shop - Invoice no. {order.id}"
    message = "Please, find attached the invoice for your recent purchase."
    email = EmailMessage(subject, message, "admin@myshop.com", [order.email])
    # generate PDF
    html = render_to_string("orders/order/pdf.html", {"order": order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + "/css/pdf.css")]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # attach PDF file
    email.attach(f"order_{order.id}.pdf", out.getvalue(), "application/pdf")
    # send e-mail
    email.send()


@shared_task
def add_user_bonus_points(order_id: int):
    """
    Task to add bonus points to the user's account after successful payment.
    """
    order = Order.objects.get(id=order_id)
    if order.paid == "paid" and order.user and order.bonus_points > 0:
        order.user.add_bonus_points(order.bonus_points)


@shared_task
def payment_completed(order_id: int):
    """
    Task to handle all post-payment actions.
    Calls other specialized tasks.
    """
    # Queue the invoice email task
    send_order_invoice.delay(order_id)

    # Queue the bonus points task
    add_user_bonus_points.delay(order_id)
