from django import forms

from .models import Promotion


class PlanChoiceForm(forms.Form):
    plan = forms.ChoiceField(
        choices=Promotion.Plan.choices, widget=forms.RadioSelect, label="Müddət seçin"
    )
