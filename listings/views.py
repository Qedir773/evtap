from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .filters import ListingFilter
from .forms import (
    LISTING_IMAGE_FORMSET_ERROR_MESSAGES,
    ListingForm,
    ListingImageFormSet,
)
from .models import Category, Favorite, Listing


class CategoryListView(ListView):
    model = Listing
    template_name = "listings/listing_list.html"
    context_object_name = "listings"
    paginate_by = 20

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        qs = Listing.objects.approved().filter(category=self.category).prefetch_related("images")
        self.filterset = ListingFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["filter"] = self.filterset
        return context


class ListingSearchView(ListView):
    model = Listing
    template_name = "listings/listing_list.html"
    context_object_name = "listings"
    paginate_by = 20

    def get_queryset(self):
        qs = Listing.objects.approved().prefetch_related("images")
        self.filterset = ListingFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class ListingDetailView(DetailView):
    model = Listing
    template_name = "listings/listing_detail.html"
    context_object_name = "listing"

    def get_queryset(self):
        return Listing.objects.all().prefetch_related("images")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status != Listing.Status.APPROVED:
            is_owner = self.request.user.is_authenticated and obj.owner_id == self.request.user.id
            is_staff = self.request.user.is_authenticated and self.request.user.is_staff
            if not (is_owner or is_staff):
                from django.http import Http404

                raise Http404("Elan tapılmadı")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = self.object

        viewed_key = "viewed_listings"
        viewed = self.request.session.get(viewed_key, [])
        if listing.pk not in viewed:
            listing.views_count += 1
            listing.save(update_fields=["views_count"])
            viewed.append(listing.pk)
            self.request.session[viewed_key] = viewed

        context["similar_listings"] = (
            Listing.objects.approved()
            .filter(category=listing.category, region=listing.region)
            .exclude(pk=listing.pk)
            .prefetch_related("images")[:4]
        )
        if self.request.user.is_authenticated:
            context["is_favorited"] = Favorite.objects.filter(
                user=self.request.user, listing=listing
            ).exists()
        return context


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = "listings/listing_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ListingImageFormSet(
                self.request.POST,
                self.request.FILES,
                error_messages=LISTING_IMAGE_FORMSET_ERROR_MESSAGES,
            )
        else:
            context["image_formset"] = ListingImageFormSet(
                error_messages=LISTING_IMAGE_FORMSET_ERROR_MESSAGES
            )
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = Listing.Status.PENDING
        context = self.get_context_data()
        image_formset = context["image_formset"]
        if image_formset.is_valid():
            response = super().form_valid(form)
            image_formset.instance = self.object
            image_formset.save()
            messages.success(
                self.request, "Elanınız yoxlama üçün göndərildi."
            )
            return response
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("listings:my_listings")


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = "listings/listing_form.html"

    def test_func(self):
        listing = self.get_object()
        return self.request.user.is_staff or listing.owner_id == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ListingImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                error_messages=LISTING_IMAGE_FORMSET_ERROR_MESSAGES,
            )
        else:
            context["image_formset"] = ListingImageFormSet(
                instance=self.object, error_messages=LISTING_IMAGE_FORMSET_ERROR_MESSAGES
            )
        return context

    def form_valid(self, form):
        if form.instance.status == Listing.Status.APPROVED:
            form.instance.status = Listing.Status.PENDING
        context = self.get_context_data()
        image_formset = context["image_formset"]
        if image_formset.is_valid():
            response = super().form_valid(form)
            image_formset.instance = self.object
            image_formset.save()
            messages.success(
                self.request, "Elan yeniləndi və yenidən yoxlamaya göndərildi."
            )
            return response
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("listings:my_listings")


class MyListingsView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = "listings/my_listings.html"
    context_object_name = "listings"

    def get_queryset(self):
        return Listing.objects.filter(owner=self.request.user).prefetch_related("images")


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = "listings/favorites.html"
    context_object_name = "favorites"

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            "listing"
        ).prefetch_related("listing__images")


class FavoriteToggleView(LoginRequiredMixin, DetailView):
    model = Listing

    def post(self, request, *args, **kwargs):
        listing = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, listing=listing
        )
        if not created:
            favorite.delete()
            is_favorited = False
        else:
            is_favorited = True

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"is_favorited": is_favorited})

        next_url = request.META.get("HTTP_REFERER") or listing.get_absolute_url()
        return redirect(next_url)
