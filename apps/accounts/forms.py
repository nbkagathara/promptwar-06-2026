from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import ExamType


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm Password",
    )
    exam_type = forms.ModelChoiceField(
        queryset=ExamType.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Choose your target exam...",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match.")

        return cleaned_data


class ProfileForm(forms.Form):
    exam_type = forms.ModelChoiceField(
        queryset=ExamType.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Choose your target exam...",
    )
