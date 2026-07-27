from django import forms


class PromoCodeRedeemForm(forms.Form):
    code = forms.CharField(
        max_length=40,
        label="Promokod",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Promokodu daxil edin"}
        ),
    )
