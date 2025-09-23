from django.db import models
from django.urls import reverse
from faker import Faker
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200, help_text="Category name"),
        slug=models.SlugField(max_length=200, unique=True, help_text="Category slug"),
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:list_category", args=[self.slug])

    @classmethod
    def generate_instances(cls, count: int = 5):
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                name=faker.name(),
                slug=faker.slug(),
            )