from django import forms
from django.forms import ModelForm

from .models import Color
from accounts.models import CustomUser


class ProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ImportForm(forms.Form):
    """Form for importing zip files"""

    zip_file = forms.FileField(
        widget=forms.FileInput(attrs={"accept": ".zip", "class": "form-control"})
    )

    def clean_zip_file(self):
        zip_file = self.cleaned_data["zip_file"]
        if not zip_file.name.endswith(".zip"):
            raise forms.ValidationError("Please upload a ZIP file.")
        return zip_file


class ColorUpdateForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name", "hex_value"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "hex_value": forms.TextInput(
                attrs={"type": "color", "class": "form-control form-control-color"}
            ),
        }
