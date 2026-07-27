from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from listings.models import Listing

from . import services
from .forms import PromoCodeRedeemForm


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        listing = get_object_or_404(Listing, pk=self.kwargs["pk"])
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or listing.owner_id == self.request.user.id
        )


class RedeemPromoCodeView(LoginRequiredMixin, View):
    def post(self, request):
        form = PromoCodeRedeemForm(request.POST)
        if form.is_valid():
            try:
                amount = services.redeem_promocode(request.user, form.cleaned_data["code"])
                messages.success(request, f"{amount} token balansınıza əlavə edildi.")
            except services.PromoCodeError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Promokodu düzgün daxil edin.")
        return redirect("accounts:dashboard")


def _back_to(request, listing):
    next_url = request.META.get("HTTP_REFERER") or listing.get_absolute_url()
    return redirect(next_url)


class BumpListingView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        try:
            services.bump_listing(request.user, listing)
            messages.success(request, "Elan irəli çəkildi.")
        except services.InsufficientBalanceError as exc:
            messages.error(request, str(exc))
        return _back_to(request, listing)


class ActivateVipView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        service_type = request.POST.get("service_type", "")
        try:
            services.activate_vip(request.user, listing, service_type)
            messages.success(request, "Elan VIP edildi.")
        except services.InsufficientBalanceError as exc:
            messages.error(request, str(exc))
        except ValueError as exc:
            messages.error(request, str(exc))
        return _back_to(request, listing)


class ActivateUrgentView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        try:
            services.activate_urgent(request.user, listing)
            messages.success(request, "Elan təcili olaraq işarələndi.")
        except services.InsufficientBalanceError as exc:
            messages.error(request, str(exc))
        return _back_to(request, listing)
