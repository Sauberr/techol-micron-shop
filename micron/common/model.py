from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE


class TimeStampedModel(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Date and time when product was created"),
                                      db_index=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      help_text=_("Date and time when product was last updated"), db_index=True)

    class Meta:
        abstract = True