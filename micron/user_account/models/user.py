from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE

from user_account.managers import CustomUserManager


class User(SafeDeleteModel, AbstractUser):
    """Custom User model"""
    _safedelete_policy = SOFT_DELETE

    objects = CustomUserManager()

    image = models.ImageField(upload_to="avatar", null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)
    favorite_products = models.ManyToManyField("products.Product", blank=True)
    bonus_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username

    def add_bonus_points(self, points: float) -> None:
        self.bonus_points += points
        self.save()