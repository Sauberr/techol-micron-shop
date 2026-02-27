from products.models import Category
from products.utils.currency import get_usd_to_uah_rate


def categories(request) -> dict:
    """Provides all categories to all templates."""
    all_categories = Category.objects.all()
    return {"all_categories": all_categories}


def currency_rate(request) -> dict:
    """
    Provides the current USD→UAH exchange rate and current language
    to all templates. Rate is fetched from NBU API and cached for 1 hour.
    """
    rate = get_usd_to_uah_rate()
    language = getattr(request, "LANGUAGE_CODE", "en")
    return {
        "usd_to_uah_rate": rate,
        "current_language": language,
    }

