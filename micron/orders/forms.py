from django import forms
from orders.models.order import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
        exclude = [
            "user",
        ]
