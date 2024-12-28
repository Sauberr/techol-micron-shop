from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


class User(AbstractUser):
    image = models.ImageField(upload_to="avatar", null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)
    favorite_products = models.ManyToManyField("products.Product", blank=True)

    class Meta:
        verbose_name: str = "User"
        verbose_name_plural: str = "Users"

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    image = models.ImageField(upload_to="avatar", null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name: str = "Profile"
        verbose_name_plural: str = "Profiles"

    def __str__(self):
        return self.user.username


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    class Meta:
        verbose_name: str = "Email Verification"
        verbose_name_plural: str = "Email Verifications"

    def __str__(self):
        return f"EmailVerification object for {self.user.email}"

    def send_verification_email(self):
        link = reverse(
            "user_account:email_verification",
            kwargs={"email": self.user.email, "code": self.code},
        )
        verification_link = f"{settings.DOMAIN_NAME}{link}"
        subject = f"Account Verification for {self.user.username}"
        message = "Follow the link to verify {} for {}".format(
            verification_link, self.user.email
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return True if now() >= self.expiration else False


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = CKEditor5Field(config_name='extends')

    class Meta:
        verbose_name: str = "Contact"
        verbose_name_plural: str = "Contacts"

    def __str__(self):
        return self.name
