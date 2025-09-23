from django import forms
from products.models.review import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["stars", "text"]
