from parler.managers import TranslatableManager, TranslatableQuerySet
from safedelete.managers import SafeDeleteManager
from safedelete.queryset import SafeDeleteQueryset


class SafeDeleteTranslatableQuerySet(SafeDeleteQueryset, TranslatableQuerySet):
    """
    A custom QuerySet combining SafeDelete and Parler.
    Use soft delete with model translations.
    """
    pass


class SafeDeleteTranslatableManager(SafeDeleteManager, TranslatableManager):
    """
    A custom manager that integrates SafeDelete and Parler.
    Used for the Product and Category models.
    """
    _queryset_class = SafeDeleteTranslatableQuerySet
