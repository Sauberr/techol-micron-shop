from celery import shared_task
from django.core.mail import send_mail
from orders.models.order import Order
import logging
from tg_bot.notifier import notify_order_created
from tg_bot.notifier import notify_order_paid

logger = logging.getLogger(__name__)


@shared_task
def order_created_email(order_id: int) -> int:
    """Send email notification when order is created."""
    order = Order.objects.get(id=order_id)
    subject = f"Order nr. {order.id}"
    message = (
        f"Dear {order.first_name}, \n\n"
        f"You have successfully placed an order."
        f"Your order ID is {order.id}."
    )
    try:
        return send_mail(subject, message, "admin@micrion.com", [order.email])
    except Exception as exc:
        logger.warning("Failed to send order email for order %s: %s", order_id, exc)
        return 0


@shared_task
def order_created_telegram(order_id: int) -> None:
    """Send Telegram notification to admin when order is created."""
    order = Order.objects.prefetch_related("items__product", "coupon").get(id=order_id)
    notify_order_created(order)


@shared_task
def send_telegram_order_paid(order_id: int) -> None:
    """Send Telegram notification to admin when order is paid."""
    order = Order.objects.prefetch_related("items__product", "coupon").get(id=order_id)
    notify_order_paid(order)
