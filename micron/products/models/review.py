import html
import bleach
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field
from faker import Faker

from common.model import TimeStampedModel
from products.models.product import Product

_ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's',
    'a', 'ul', 'ol', 'li', 'blockquote',
    'h1', 'h2', 'h3', 'code', 'pre',
    'sub', 'sup', 'span', 'mark',
    'figure', 'img', 'figcaption',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]
_ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    '*': ['class'],
}


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

    def save(self, *args, **kwargs):
        self.text = bleach.clean(
            html.unescape(self.text),
            tags=_ALLOWED_TAGS,
            attributes=_ALLOWED_ATTRS,
            strip=True,
        )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user}"

    @classmethod
    def generate_instances(cls, count: int = 5) -> None:
        faker = Faker()
        for __ in range(count):
            cls.objects.create(
                user=get_user_model().objects.first(),
                product=Product.objects.first(),
                stars=faker.random_int(1, 5),
                text=faker.text(),
            )
