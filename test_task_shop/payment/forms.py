from django import forms
from payment.models import ShippingAddress


class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('full_name', 'email', 'street_address', 'apartment_address', 'city', 'country', 'zip')


