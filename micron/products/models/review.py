from django.contrib.auth import get_user_model
from django.db import models

from django_ckeditor_5.fields import CKEditor5Field
from faker import Faker
from user_account.models import User
from products.models.product import Product


class Review(models.Model):
    STARS_CHOICES = (
        (1, "★☆☆☆☆"),
        (2, "★★☆☆☆"),
        (3, "★★★☆☆"),
        (4, "★★★★☆"),
        (5, "★★★★★"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    stars = models.IntegerField(choices=STARS_CHOICES)
    text = CKEditor5Field(config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.user}"

    @classmethod
    def generate_instances(cls, count: int = 5):
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                user=User.objects.first(),
                product=Product.objects.first(),
                stars=faker.random_int(1, 5),
                text=faker.text(),
            )
