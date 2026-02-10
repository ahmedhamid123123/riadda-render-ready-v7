from django import forms
from .models import Price

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['denomination', 'price_to_agent', 'is_active']

