from typing import Any

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms



class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = False
        self.fields['password1'].help_text = False
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already used")
        return email


