from django.views.generic import TemplateView

from listings.forms import ListingSearchForm
from listings.models import Category, Listing


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ListingSearchForm()
        context["categories"] = Category.objects.all()
        context["featured_listings"] = Listing.objects.currently_featured().prefetch_related("images")[:8]
        context["latest_listings"] = (
            Listing.objects.approved().order_by("-created_at").prefetch_related("images")[:12]
        )
        return context
