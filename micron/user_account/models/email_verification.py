from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class EmailVerification(models.Model):
    """Model for email verification codes."""
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    class Meta:
        verbose_name = _("Email Verification")
        verbose_name_plural = _("Email Verifications")

    def __str__(self) -> str:
        return f"EmailVerification object for {self.user.email}"

    def send_verification_email(self) -> None:
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

    def is_expired(self) -> bool:
        return True if now() >= self.expiration else False
