from decimal import Decimal

from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from faker import Faker
from parler.models import TranslatableModel, TranslatedFields
from taggit.managers import TaggableManager
from products.models.category import Category
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            max_length=200,
            help_text=_("Product name")
        ),
        slug=models.SlugField(
            max_length=200,
            help_text=_("Product URL slug")
        ),
        description=CKEditor5Field(
            config_name='extends',
            blank=True,
            null=True,
            help_text=_("Detailed product description")
        ),
    )
    category = models.ForeignKey(
        "Category",
        related_name="products",
        on_delete=models.CASCADE,
        help_text=_("Product category")
    )
    image = models.ImageField(
        upload_to="products",
        help_text=_("Product image")
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Product price (minimum 0.01)")
    )
    price_with_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Discounted price (minimum 0.01)")
    )
    bonus_points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Bonus points earned from this product (non-negative)")
    )
    available = models.BooleanField(
        default=True,
        help_text=_("Is product available for purchase")
    )
    discount = models.BooleanField(
        default=False,
        help_text=_("Is product on discount")
    )
    quantity = models.PositiveIntegerField(
        default=0,
        help_text=_("Available quantity in stock")
    )
    tags = TaggableManager(
        blank=True,
        help_text=_("Product tags for categorization")
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date and time when product was created")
    )
    updated = models.DateTimeField(
        auto_now=True,
        help_text=_("Date and time when product was last updated")
    )

    class Meta:
        indexes = [
            models.Index(fields=["-created"]),
        ]
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        if self.price:
            if self.discount and self.price_with_discount:
                self.bonus_points = self.price_with_discount * Decimal(0.3)
            else:
                self.bonus_points = self.price * Decimal(0.3)
        super().save(*args, **kwargs)


    def get_absolute_url(self) -> str:
        return reverse("products:product_detail", args=[self.slug])

    @classmethod
    def generate_instances(cls, count: int) -> None:
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                name=faker.name(),
                slug=faker.slug(),
                description=faker.text(),
                price=faker.random_int(10, 100),
                image="products/default.jpg",
                category=Category.objects.first(),
            )

