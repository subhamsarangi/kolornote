from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import pytz

from .models import CustomUser


class EmailRegistrationForm(UserCreationForm):
    timezone = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ("email", "timezone")  # Note: password handled by UserCreationForm

    def clean_email(self):
        print(self.cleaned_data, "self.cleaned_data----------------")
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists. Try logging in."
            )
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"autofocus": True})
        self.fields["timezone"].widget = forms.HiddenInput()


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"autofocus": True})
    )

    device_timezone = forms.CharField(widget=forms.HiddenInput(), required=False)
