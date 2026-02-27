import logging
from typing import Union

import httpx
from django.core.cache import cache

logger = logging.getLogger(__name__)

NBU_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json"
CACHE_KEY = "usd_to_uah_rate"
CACHE_TIMEOUT = 60 * 60


def get_usd_to_uah_rate() -> Union[float, None]:
    """
    Fetch USD→UAH exchange rate from the National Bank of Ukraine API.
    Result is cached in Redis for 1 hour.
    Returns None if fetch fails.
    """
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return float(cached)

    try:
        response = httpx.get(NBU_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        rate = float(data[0]["rate"])
        cache.set(CACHE_KEY, rate, CACHE_TIMEOUT)
        logger.info("Fetched USD→UAH rate: %.4f", rate)
        return rate
    except Exception as exc:
        logger.warning("Failed to fetch USD→UAH rate: %s", exc)
        return None


