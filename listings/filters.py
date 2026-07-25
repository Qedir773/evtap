from django import forms
import django_filters

from .models import Category, Listing

_TEXT = forms.TextInput(attrs={"class": "form-control form-control-sm"})
_NUMBER = forms.NumberInput(attrs={"class": "form-control form-control-sm"})
_SELECT = forms.Select(attrs={"class": "form-select form-select-sm"})

SORT_CHOICES = (
    ("-created_at", "Ən son əlavə edilənlər"),
    ("price", "Əvvəlcə ucuz"),
    ("-price", "Əvvəlcə bahalı"),
    ("-views_count", "Ən çox baxılan"),
)


class _SortSelect(forms.Select):
    """OrderingFilter requires a widget *class* (it wraps it for CSV support),
    so attrs are baked in here rather than passed as an instance."""

    def __init__(self, attrs=None, choices=()):
        merged_attrs = {"class": "form-select form-select-sm evtap-sort-select"}
        if attrs:
            merged_attrs.update(attrs)
        super().__init__(attrs=merged_attrs, choices=choices)


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
    sort = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("price", "price"),
            ("views_count", "views_count"),
        ),
        choices=SORT_CHOICES,
        empty_label=None,
        widget=_SortSelect,
    )

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
