from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    image = models.ImageField(upload_to="avatar", null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)
    favorite_products = models.ManyToManyField("products.Product", blank=True)
    bonus_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    def add_bonus_points(self, points: float) -> None:
        self.bonus_points += points
        self.save()