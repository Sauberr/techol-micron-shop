import asyncio
import logging
from typing import TYPE_CHECKING

from django.conf import settings

from .bot import bot

if TYPE_CHECKING:
    from orders.models.order import Order

logger = logging.getLogger(__name__)


def _build_order_message(order: "Order", paid: bool = False) -> str:
    """Build order notification message."""

    items_lines = ""
    for item in order.items.select_related("product").all():
        product_name = item.product.safe_translation_getter("name", any_language=True) or str(item.product)
        items_lines += (
            f"  • <b>{product_name}</b> — "
            f"{item.quantity} pcs. × ${item.price:.2f} = <b>${item.get_cost():.2f}</b>\n"
        )

    if not items_lines:
        items_lines = "  (no items)\n"

    discount_line = ""
    if order.discount:
        discount_line = f"🏷 <b>Discount:</b> {order.discount}% (−${order.get_discount():.2f})\n"

    coupon_line = ""
    if order.coupon:
        coupon_line = f"🎟 <b>Coupon:</b> <code>{order.coupon.code}</code>\n"

    bonus_line = ""
    if order.bonus_points:
        bonus_line = f"⭐️ <b>Bonus points:</b> {order.bonus_points}\n"

    if paid:
        header = "✅ <b>Order #{id} — PAID</b>".format(id=order.id)
    else:
        header = "🆕 <b>Order #{id} — CREATED</b>".format(id=order.id)

    message = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Customer:</b> {order.first_name} {order.last_name}\n"
        f"📧 <b>Email:</b> {order.email}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Items:</b>\n"
        f"{items_lines}"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{coupon_line}"
        f"{discount_line}"
        f"{bonus_line}"
        f"💰 <b>Total:</b> <b>${order.get_total_cost():.2f}</b>\n"
        f"📅 <b>Date:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"📍 <b>Address:</b> {order.region}, {order.city}, {order.post_office}\n"
    )

    if paid and order.stripe_id:
        message += f"\n🔗 <a href='{order.get_stripe_url()}'>View payment in Stripe</a>"

    return message


async def _send(text: str) -> None:
    try:
        await bot.send_message(
            chat_id=settings.ADMIN_TELEGRAM_ID,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.warning("Failed to send Telegram notification: %s", exc)


def notify_order_created(order: "Order") -> None:
    """Called from Celery task when order is created."""
    asyncio.run(_send(_build_order_message(order, paid=False)))


def notify_order_paid(order: "Order") -> None:
    """Called from Celery task when order is paid via Stripe."""
    asyncio.run(_send(_build_order_message(order, paid=True)))


def create_customer_message(order):
    message = (
        f"<b>New Order #{order.id}!</b>\n"
        f"👤 <b>Customer:</b> {order.first_name} {order.last_name}\n"
        f"✉️ <b>Email:</b> {order.email}\n"
        f"📍 <b>Delivery:</b> {order.region}, {order.city}, {order.post_office}\n"
        f"💰 <b>Total price:</b> ${order.get_total_cost()}\n"
    )

    return message
