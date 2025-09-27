from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from common.model import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Contact(TimeStampedModel):
    name = models.CharField(max_length=100, help_text=_("Write Full Name"))
    email = models.EmailField(help_text=_("Write Your Email"))
    message = CKEditor5Field(config_name='extends', help_text=_("Write Your Message"), max_length=2000)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return self.name