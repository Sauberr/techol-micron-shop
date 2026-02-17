from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from faker import Faker
from parler.models import TranslatableModel, TranslatedFields
from safedelete.models import SOFT_DELETE_CASCADE
from django.utils.translation import gettext_lazy as _

from common.model import TimeStampedModel
from products.managers import SafeDeleteTranslatableManager


class Category(TimeStampedModel, TranslatableModel):
    """Category model"""
    _safedelete_policy = SOFT_DELETE_CASCADE

    objects = SafeDeleteTranslatableManager()

    translations = TranslatedFields(
        name=models.CharField(max_length=200, help_text="Category name"),
        slug=models.SlugField(max_length=200, help_text="Category slug"),
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name

    def clean(self) -> None:
        super().clean()

        current_language = self.get_current_language()
        if hasattr(self, 'slug'):
            existing = Category.objects.filter(
                translations__slug=self.slug,
                translations__language_code=current_language
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({
                    'slug': _("Category with this slug already exists for this language.")
                })

    def get_absolute_url(self) -> str:
        return reverse("products:products") + f"?category={self.slug}"

    @classmethod
    def generate_instances(cls, count: int = 5) -> None:
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                name=faker.name(),
                slug=faker.slug(),
            )
