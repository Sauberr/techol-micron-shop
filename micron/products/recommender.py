import logging

from django_redis import get_redis_connection
from products.models.product import Product

logger = logging.getLogger("main")


class Recommender:
    """Recommender system for products based on purchase history."""

    def __init__(self):
        """Initialize Redis connection from django-redis pool."""
        try:
            self.r = get_redis_connection("default")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.r = None

    @staticmethod
    def get_product_key(product_id: int) -> str:
        """Generate Redis key for a product's purchased_with data."""
        return f"product:{product_id}:purchased_with"

    def products_bought(self, products: list[Product]) -> None:
        """Record products bought together in Redis sorted sets."""
        if not self.r:
            return

        try:
            product_ids = [p.id for p in products]
            for product_id in product_ids:
                for with_id in product_ids:
                    if product_id != with_id:
                        self.r.zincrby(self.get_product_key(product_id), 1, with_id)
        except Exception as e:
            logger.error(f"Failed to record products bought: {e}")

    def suggest_products_for(self, products: list[Product], max_results: int = 6) -> list[Product]:
        """Suggest products based on products bought together."""

        if not self.r:
            return []

        try:
            product_ids = [p.id for p in products]

            if len(products) == 1:
                suggestions = self.r.zrange(
                    self.get_product_key(product_ids[0]), 0, -1, desc=True
                )[:max_results]
            else:
                tmp_key = f"tmp_{'_'.join(map(str, product_ids))}"
                keys = [self.get_product_key(pid) for pid in product_ids]
                self.r.zunionstore(tmp_key, keys)
                self.r.zrem(tmp_key, *product_ids)
                suggestions = self.r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
                self.r.delete(tmp_key)

            suggested_product_ids = [int(pid) for pid in suggestions]
            suggested_products = list(Product.objects.filter(id__in=suggested_product_ids))
            suggested_products.sort(key=lambda x: suggested_product_ids.index(x.id))
            return suggested_products

        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []

    def clear_purchases(self) -> None:
        """Clear all purchase data from Redis."""
        if not self.r:
            return

        try:
            for product_id in Product.objects.values_list("id", flat=True):
                self.r.delete(self.get_product_key(product_id))
        except Exception as e:
            logger.error(f"Failed to clear purchases: {e}")
