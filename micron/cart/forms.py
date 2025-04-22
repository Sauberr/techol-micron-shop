from django import forms
from django.utils.translation import gettext_lazy as _

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        label=_("Quantity"),
        widget=forms.Select(
            attrs={
                "class": "form-control text-center me-3",
            }
        ),
    )
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)

        if product and hasattr(product, 'quantity'):
            max_qty = min(product.quantity, 20)

            if max_qty > 0:
                choices = [(i, str(i)) for i in range(1, max_qty + 1)]
                self.fields['quantity'].choices = choices
            else:
                self.fields['quantity'].choices = [(0, _("Out of stock"))]
                self.fields['quantity'].disabled = True

        else:
            self.fields['quantity'].choices = [(i, str(i)) for i in range(1, 21)]

