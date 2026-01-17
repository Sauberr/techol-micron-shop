from decimal import Decimal

from django.contrib.auth import get_user_model

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.model import TimeStampedModel

STATUS = (
    ("paid", _("Paid")),
    ("unpaid", _("Unpaid")),
)

class Order(TimeStampedModel):
    """Order Model"""
    first_name = models.CharField(_("first_name"), max_length=50)
    last_name = models.CharField(_("last_name"), max_length=50)
    email = models.EmailField(_("email"))
    address = models.CharField(_("address"), max_length=250)
    postal_code = models.CharField(_("postal_code"), max_length=20)
    city = models.CharField(_("city"), max_length=100)
    paid = models.CharField(choices=STATUS, max_length=10, default="unpaid")
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(
        "coupons.Coupon", related_name="orders", null=True, blank=True, on_delete=models.SET_NULL
    )
    bonus_points = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))]
    )
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at", "-updated_at"]


    def __str__(self) -> str:
        return f"Order {self.id}"

    def get_discount(self) -> Decimal:
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self) -> Decimal:
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def get_total_cost_before_discount(self) -> Decimal:
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self)-> str:
        if not self.stripe_id:
            return ""
        if "_test_" in settings.STRIPE_SECRET_KEY:
            path = "/test/"
        else:
            path = "/"
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"
