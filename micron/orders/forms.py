from django import forms
from orders.models.order import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "region", "city", "post_office"]
        exclude = ["user"]
        widgets = {
            "region": forms.HiddenInput(attrs={"id": "id_region_hidden"}),
            "city": forms.HiddenInput(attrs={"id": "id_city_hidden"}),
            "post_office": forms.HiddenInput(attrs={"id": "id_post_office_hidden"}),
        }
