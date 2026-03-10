import logging
import uuid
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from user_account.models.email_verification import EmailVerification

logger = logging.getLogger(__name__)


@shared_task
def send_email_verification(user_id: int) -> None:
    user = get_user_model().objects.get(id=user_id)
    expiration = now() + timedelta(hours=48)
    record = EmailVerification.objects.create(
        code=uuid.uuid4(), user=user, expiration=expiration
    )

    try:
        record.send_verification_email()
    except Exception as e:
        logger.error(f"Failed to send verification email for user {user_id}: {e}")



