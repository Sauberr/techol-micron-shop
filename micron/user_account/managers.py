from safedelete.managers import SafeDeleteManager
from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager, SafeDeleteManager):
    """
    Custom manager for User model that combines Django's UserManager
    """
    _safedelete_visibility = SafeDeleteManager._safedelete_visibility