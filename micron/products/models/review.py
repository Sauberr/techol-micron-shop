from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field
from faker import Faker

from common.model import TimeStampedModel
from user_account.models import User
from products.models.product import Product


class Review(TimeStampedModel):
    """Product Review Model"""
    STARS_CHOICES = (
        (1, "★☆☆☆☆"),
        (2, "★★☆☆☆"),
        (3, "★★★☆☆"),
        (4, "★★★★☆"),
        (5, "★★★★★"),
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True
    )
    stars = models.IntegerField(choices=STARS_CHOICES)
    text = CKEditor5Field(config_name='extends')

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")

    def __str__(self) -> str:
        return f"{self.user}"

    @classmethod
    def generate_instances(cls, count: int = 5) -> None:
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                user=User.objects.first(),
                product=Product.objects.first(),
                stars=faker.random_int(1, 5),
                text=faker.text(),
            )
