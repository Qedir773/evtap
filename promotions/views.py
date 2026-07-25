from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from listings.models import Listing

from .forms import PlanChoiceForm
from .models import PLAN_PRICES, Promotion


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        listing = get_object_or_404(Listing, pk=self.kwargs["pk"])
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or listing.owner_id == self.request.user.id
        )


def _plan_options():
    return [
        {"value": value, "label": label, "price": PLAN_PRICES[value]}
        for value, label in Promotion.Plan.choices
    ]


class BoostListingView(LoginRequiredMixin, OwnerRequiredMixin, View):
    template_name = "promotions/boost.html"

    def get(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        form = PlanChoiceForm()
        return render(
            request,
            self.template_name,
            {"listing": listing, "form": form, "plan_options": _plan_options()},
        )

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        form = PlanChoiceForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data["plan"]
            promotion = Promotion.objects.create(
                listing=listing,
                user=request.user,
                plan=plan,
                amount=PLAN_PRICES[plan],
            )
            return redirect("promotions:mock_payment", pk=promotion.pk)
        return render(
            request,
            self.template_name,
            {"listing": listing, "form": form, "plan_options": _plan_options()},
        )


class MockPaymentView(LoginRequiredMixin, View):
    template_name = "promotions/mock_payment.html"

    def get(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk, user=request.user)
        return render(request, self.template_name, {"promotion": promotion})

    def post(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk, user=request.user)
        if promotion.status == Promotion.Status.PENDING:
            promotion.mark_paid()
        return redirect("promotions:payment_success", pk=promotion.pk)


class PaymentSuccessView(LoginRequiredMixin, View):
    template_name = "promotions/payment_success.html"

    def get(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk, user=request.user)
        return render(request, self.template_name, {"promotion": promotion})
