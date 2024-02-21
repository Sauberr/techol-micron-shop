from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now


class User(AbstractUser):
    image = models.ImageField(upload_to="avatar", null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)
    favorite_products = models.ManyToManyField("products.Product", blank=True)


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

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
    message = models.TextField()

    def __str__(self):
        return self.name
