from django import forms
import django_filters

from .models import Category, Listing

_TEXT = forms.TextInput(attrs={"class": "form-control form-control-sm"})
_NUMBER = forms.NumberInput(attrs={"class": "form-control form-control-sm"})
_SELECT = forms.Select(attrs={"class": "form-select form-select-sm"})


class ListingFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_keyword", label="Axtarış", widget=_TEXT)
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(), widget=_SELECT
    )
    transaction_type = django_filters.ChoiceFilter(
        choices=Listing.TransactionType.choices, widget=_SELECT
    )
    region = django_filters.CharFilter(lookup_expr="iexact", widget=_TEXT)
    district = django_filters.CharFilter(lookup_expr="iexact", widget=_TEXT)
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte", widget=_NUMBER)
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte", widget=_NUMBER)
    rooms = django_filters.NumberFilter(field_name="rooms", lookup_expr="exact", widget=_NUMBER)
    area_min = django_filters.NumberFilter(field_name="area_m2", lookup_expr="gte", widget=_NUMBER)
    area_max = django_filters.NumberFilter(field_name="area_m2", lookup_expr="lte", widget=_NUMBER)

    class Meta:
        model = Listing
        fields = [
            "q",
            "category",
            "transaction_type",
            "region",
            "district",
            "price_min",
            "price_max",
            "rooms",
            "area_min",
            "area_max",
        ]

    def filter_keyword(self, queryset, name, value):
        from django.db.models import Q

        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
