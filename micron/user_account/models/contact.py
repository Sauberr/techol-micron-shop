from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = CKEditor5Field(config_name='extends')

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return self.name