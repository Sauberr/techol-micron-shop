from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from faker import Faker
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.model import TimeStampedModel


class Coupon(TimeStampedModel):
    """Coupon model"""
    code = models.CharField(max_length=50, help_text=_("Unique coupon code (for example: SAVE20, SUMMER2024)"))
    valid_from = models.DateTimeField(help_text=_("Start date and time when the coupon becomes valid"))
    valid_to = models.DateTimeField(help_text=_("End date and time when the coupon expires"))
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Percentage value (0 to 100)"),
    )
    active = models.BooleanField(default=False, help_text=_("Designates whether this coupon is active"))

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")

    def __str__(self) -> str:
        return self.code

    def clean(self) -> None:
        super().clean()
        if self.valid_to <= self.valid_from:
            raise ValidationError(_("The 'valid_to' date must be after the 'valid_from' date."))

        # Проверяем уникальность кода среди активных (не удалённых) купонов
        existing_coupon = Coupon.objects.filter(code=self.code).exclude(pk=self.pk)
        if existing_coupon.exists():
            raise ValidationError(_("Coupon with this code already exists."))

    @classmethod
    def generate_instances(cls, count: int = 5) -> None:
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                code=faker.name(),
                valid_from=faker.date_time_this_year(),
                valid_to=faker.date_time_this_year(),
                discount=faker.random_int(1, 100),
                active=faker.boolean(),
            )
