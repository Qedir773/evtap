from django.views.generic import TemplateView

from django.db.models import F

from listings.filters import SORT_CHOICES
from listings.forms import ListingSearchForm
from listings.models import Category, Listing

_VALID_SORTS = {value for value, _label in SORT_CHOICES}


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ListingSearchForm()
        context["categories"] = Category.objects.all()
        context["vip_listings"] = Listing.objects.currently_vip().prefetch_related("images")[:8]

        sort = self.request.GET.get("sort")
        if sort not in _VALID_SORTS:
            sort = "-created_at"
        context["current_sort"] = sort
        context["sort_choices"] = SORT_CHOICES
        context["latest_listings"] = (
            Listing.objects.approved()
            .order_by("-is_vip", "-is_urgent", F("last_bumped_at").desc(nulls_last=True), sort)
            .prefetch_related("images")[:12]
        )
        return context
