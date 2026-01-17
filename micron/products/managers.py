from parler.managers import TranslatableManager, TranslatableQuerySet
from safedelete.managers import SafeDeleteManager
from safedelete.queryset import SafeDeleteQueryset


class SafeDeleteTranslatableQuerySet(SafeDeleteQueryset, TranslatableQuerySet):
    """
    Кастомный QuerySet, объединяющий SafeDelete и Parler.
    Позволяет использовать мягкое удаление с переводами моделей.
    """
    pass


class SafeDeleteTranslatableManager(SafeDeleteManager, TranslatableManager):
    """
    Кастомный Manager, объединяющий SafeDelete и Parler.
    Используется для моделей Product и Category.
    """
    _queryset_class = SafeDeleteTranslatableQuerySet
