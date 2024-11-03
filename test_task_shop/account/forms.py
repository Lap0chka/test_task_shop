from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    """
    A form for user registration, extending the UserCreationForm to include an email field.
    """

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the UserRegisterForm, setting email as a required field and
        disabling help text for username and password fields.
        """
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields["username"].help_text = False
        self.fields["password1"].help_text = False
        self.fields["email"].required = True

    def clean_email(self) -> str:
        """
        Validates the email field to ensure uniqueness. Converts the email to lowercase
        before saving and raises a validation error if the email already exists in the database.
        """
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already used")
        return email
