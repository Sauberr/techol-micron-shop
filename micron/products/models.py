from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields
from user_account.models import User
from django_ckeditor_5.fields import CKEditor5Field


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200, unique=True),
    )

    class Meta:
        # ordering = ['name']
        # indexes = [
        # models.Index(fields=['name']),
        # ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:list_category", args=[self.slug])


class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200),
        description=CKEditor5Field(config_name='extends', blank=True, null=True),
    )
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_with_discount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    available = models.BooleanField(default=True)
    discount = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ['name']
        indexes = [
            # models.Index(fields=['id', 'slug']),
            # models.Index(fields=['name']),
            models.Index(fields=["-created"]),
        ]
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.slug])


class Review(models.Model):
    STARS_CHOICES = (
        (1, "★☆☆☆☆"),
        (2, "★★☆☆☆"),
        (3, "★★★☆☆"),
        (4, "★★★★☆"),
        (5, "★★★★★"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=STARS_CHOICES)
    text = CKEditor5Field(config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.user}"