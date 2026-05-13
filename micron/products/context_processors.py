from django.core.cache import cache

from products.models import Category
from products.utils.currency import get_usd_to_uah_rate

_CATEGORIES_CACHE_KEY = "all_categories"
_CATEGORIES_CACHE_TIMEOUT = 60 * 10


def categories(request) -> dict:
    """Provides all categories to all templates."""
    all_categories = cache.get(_CATEGORIES_CACHE_KEY)
    if all_categories is None:
        all_categories = list(Category.objects.all())
        cache.set(_CATEGORIES_CACHE_KEY, all_categories, _CATEGORIES_CACHE_TIMEOUT)
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

