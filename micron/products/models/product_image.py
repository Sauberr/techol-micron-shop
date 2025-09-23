from django.db import models


class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/additional/')

    class Meta:
        verbose_name = 'product image'
        verbose_name_plural = 'product images'

    def __str__(self):
        return f"Image {self.product.name}"