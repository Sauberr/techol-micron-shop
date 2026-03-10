import logging

from celery import shared_task
from django.contrib.sessions.backends.db import SessionStore
from django.utils.timezone import now
from user_account.models.email_verification import EmailVerification

logger = logging.getLogger(__name__)


@shared_task
def clear_expired_sessions() -> None:
    """Deletes expired sessions from the database."""
    try:
        SessionStore.clear_expired()
        logger.info("Expired sessions cleared successfully.")
    except Exception as e:
        logger.error("Failed to clear expired sessions: %s", e)


@shared_task
def clear_expired_email_verifications() -> None:
    """Deletes expired email verification records from the database."""

    try:
        deleted_count, _ = EmailVerification.objects.filter(expiration__lt=now()).delete()
        logger.info("Deleted %d expired email verifications.", deleted_count)
    except Exception as e:
        logger.error("Failed to clear expired email verifications: %s", e)

