from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
        )  # only email field (and password handled by UserCreationForm)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists. Try logging in."
            )
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # optionally remove username help text if any
        self.fields["email"].widget.attrs.update({"autofocus": True})


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"autofocus": True})
    )
