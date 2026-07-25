from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User

from .models import Profile

USERNAME_MAX_LENGTH = 5


class RegisterForm(UserCreationForm):
    username = UsernameField(
        max_length=USERNAME_MAX_LENGTH,
        label="İstifadəçi adı",
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": USERNAME_MAX_LENGTH}),
        help_text=f"Ən çoxu {USERNAME_MAX_LENGTH} simvol.",
    )
    email = forms.EmailField(
        required=True, label="E-poçt", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone_number = forms.CharField(
        required=False, label="Telefon nömrəsi", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    is_agent = forms.BooleanField(
        required=False,
        label="Agentlik hesabı olaraq qeydiyyatdan keç",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.update_or_create(
            user=user,
            defaults={
                "phone_number": self.cleaned_data.get("phone_number", ""),
                "is_agent": self.cleaned_data.get("is_agent", False),
            },
        )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone_number", "is_agent", "agency_name", "avatar")
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "is_agent": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "agency_name": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
