from django import forms
from .models import Color


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
