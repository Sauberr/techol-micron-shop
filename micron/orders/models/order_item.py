from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE


class OrderItem(SafeDeleteModel):
    """Order Item Model"""
    _safedelete_policy = SOFT_DELETE

    order = models.ForeignKey("Order", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        "products.Product", related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self) -> str:
        return str(self.id)

    def get_cost(self) -> Decimal:
        return self.price * self.quantity
