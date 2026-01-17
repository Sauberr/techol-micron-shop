from django.contrib.auth import get_user_model
from django.db import models
from common.model import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Profile(TimeStampedModel):
    """User Profile Model"""
    user = models.OneToOneField(to=get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    image = models.ImageField(upload_to="avatar", null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self) -> str:
        return self.user.username