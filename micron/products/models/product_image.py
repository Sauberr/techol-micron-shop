from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE


class ProductImage(SafeDeleteModel):
    """Model for additional product images"""
    _safedelete_policy = SOFT_DELETE

    product = models.ForeignKey('Product', related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/additional/')

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    def __str__(self):
        return f"Image for {self.product.name}"
