from django.db import models
from django.urls import reverse
from faker import Faker
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200, unique=True),
    )

    class Meta:
        verbose_name: str = "category"
        verbose_name_plural: str = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:list_category", args=[self.slug])

    @classmethod
    def generate_instances(cls, count):
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                name=faker.name(),
                slug=faker.slug(),
            )