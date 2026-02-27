from decimal import Decimal, ROUND_HALF_UP
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def price_display(context, amount, rate=None):
    """
    Shows price in the correct currency based on the current language.
    - 'uk' → UAH (₴86 373), rounded with ROUND_HALF_UP
    - 'en' → USD ($499.99)

    Usage: {% price_display product.price %}
    """
    if amount is None:
        return ""

    language = context.get("current_language", "en")
    uah_rate = rate if rate is not None else context.get("usd_to_uah_rate")

    amount = Decimal(str(amount))

    if language == "uk" and uah_rate:
        uah = int((amount * Decimal(str(uah_rate))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return f"\u20b4{uah:,}".replace(",", "\u00a0")
    return f"${amount:,.2f}"
