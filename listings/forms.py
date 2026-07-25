from django import forms
from django.forms import inlineformset_factory

from .models import Category, Listing, ListingImage


class ListingSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Açar söz",
        widget=forms.TextInput(
            attrs={"placeholder": "Məsələn: 3 otaqlı Nəsimi", "class": "form-control"}
        ),
    )
    transaction_type = forms.ChoiceField(
        required=False,
        label="Əməliyyat növü",
        choices=[("", "Hamısı")] + list(Listing.TransactionType.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    category = forms.ModelChoiceField(
        required=False,
        label="Kateqoriya",
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    region = forms.CharField(
        required=False, label="Region", widget=forms.TextInput(attrs={"class": "form-control"})
    )


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "category",
            "title",
            "description",
            "transaction_type",
            "price",
            "currency",
            "region",
            "district",
            "address_detail",
            "rooms",
            "area_m2",
            "floor",
            "total_floors",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "transaction_type": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "currency": forms.Select(attrs={"class": "form-select"}),
            "region": forms.TextInput(attrs={"class": "form-control"}),
            "district": forms.TextInput(attrs={"class": "form-control"}),
            "address_detail": forms.TextInput(attrs={"class": "form-control"}),
            "rooms": forms.NumberInput(attrs={"class": "form-control"}),
            "area_m2": forms.NumberInput(attrs={"class": "form-control"}),
            "floor": forms.NumberInput(attrs={"class": "form-control"}),
            "total_floors": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["floor"].required = True


MAX_LISTING_IMAGES = 7


class ListingImageForm(forms.ModelForm):
    crop_box = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ListingImage
        fields = ["image", "is_cover"]
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control evtap-crop-input", "accept": "image/*"}
            ),
            "is_cover": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        crop_box = self.cleaned_data.get("crop_box")
        if crop_box:
            instance._crop_box = crop_box
        if commit:
            instance.save()
        return instance


MIN_LISTING_IMAGES = 3


class BaseListingImageFormSet(forms.BaseInlineFormSet):
    deletion_widget = forms.CheckboxInput(attrs={"class": "form-check-input"})


ListingImageFormSet = inlineformset_factory(
    Listing,
    ListingImage,
    form=ListingImageForm,
    formset=BaseListingImageFormSet,
    extra=MAX_LISTING_IMAGES,
    max_num=MAX_LISTING_IMAGES,
    validate_max=True,
    min_num=MIN_LISTING_IMAGES,
    validate_min=True,
    can_delete=True,
)

LISTING_IMAGE_FORMSET_ERROR_MESSAGES = {
    "too_few_forms": (
        f"Elan yerləşdirmək üçün ən azı {MIN_LISTING_IMAGES} şəkil yükləməlisiniz. "
        f"{MIN_LISTING_IMAGES}-dən az şəkillə elan yerləşdirilə bilməz."
    ),
}
