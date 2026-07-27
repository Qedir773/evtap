from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.shortcuts import render

from accounts.models import Profile

from . import services
from .models import PromoCode, PromotionPricing, TokenTransaction


class TokenAmountForm(forms.Form):
    amount = forms.IntegerField(min_value=1, label="Miqdar (token)")


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "transaction_type", "description", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("user__username", "user__email", "description")
    readonly_fields = ("user", "amount", "transaction_type", "description", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "token_amount",
        "max_uses",
        "current_uses",
        "is_active",
        "valid_until",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("code",)
    readonly_fields = ("current_uses", "created_at")


@admin.register(PromotionPricing)
class PromotionPricingAdmin(admin.ModelAdmin):
    list_display = ("service_type", "token_cost")
    list_display_links = ("service_type",)
    list_editable = ("token_cost",)

    def has_add_permission(self, request):
        # Xidmət növləri sabitdir (bump/vip_7/vip_10/vip_30/urgent_7) və seed
        # migration ilə yaradılıb — yeni sətir əlavə etmək yalnız təkrar
        # service_type xətasına səbəb olur, ona görə yalnız redaktəyə icazə verilir.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Profile)
class ProfileTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token_balance", "is_agent", "agency_name")
    list_display_links = ("user",)
    list_editable = ("token_balance",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user",)
    actions = ["add_tokens_action", "subtract_tokens_action", "reset_balance_action"]

    def save_model(self, request, obj, form, change):
        delta = 0
        if change and "token_balance" in form.changed_data:
            old_balance = Profile.objects.get(pk=obj.pk).token_balance
            delta = obj.token_balance - old_balance
        super().save_model(request, obj, form, change)
        if delta:
            TokenTransaction.objects.create(
                user=obj.user,
                amount=delta,
                transaction_type=TokenTransaction.Type.ADMIN_ADD,
                description="Admin: balans birbaşa redaktə edildi",
            )

    def add_tokens_action(self, request, queryset):
        return self._amount_intermediate(request, queryset, mode="add")

    add_tokens_action.short_description = "Seçilmiş istifadəçilərə token əlavə et"

    def subtract_tokens_action(self, request, queryset):
        return self._amount_intermediate(request, queryset, mode="subtract")

    subtract_tokens_action.short_description = "Seçilmiş istifadəçilərdən token çıx"

    def reset_balance_action(self, request, queryset):
        for profile in queryset:
            if profile.token_balance:
                services.add_tokens(
                    profile.user,
                    -profile.token_balance,
                    TokenTransaction.Type.ADMIN_ADD,
                    description="Admin: balans sıfırlandı",
                )
        self.message_user(request, "Seçilmiş istifadəçilərin balansı sıfırlandı.", messages.SUCCESS)

    reset_balance_action.short_description = "Seçilmiş istifadəçilərin balansını sıfırla"

    def _amount_intermediate(self, request, queryset, mode):
        action_name = "add_tokens_action" if mode == "add" else "subtract_tokens_action"

        if "apply" in request.POST:
            form = TokenAmountForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["amount"]
                signed_amount = amount if mode == "add" else -amount
                for profile in queryset:
                    if mode == "subtract" and profile.token_balance < amount:
                        self.message_user(
                            request,
                            f"{profile.user.username}: balans kifayət etmir, keçildi.",
                            messages.WARNING,
                        )
                        continue
                    services.add_tokens(
                        profile.user,
                        signed_amount,
                        TokenTransaction.Type.ADMIN_ADD,
                        description="Admin tərəfindən manual dəyişiklik",
                    )
                self.message_user(request, "Balanslar yeniləndi.", messages.SUCCESS)
                return None
        else:
            form = TokenAmountForm()

        return render(
            request,
            "admin/tokens/amount_intermediate.html",
            context={
                "profiles": queryset,
                "form": form,
                "mode": mode,
                "action_name": action_name,
                "action_checkbox_name": ACTION_CHECKBOX_NAME,
                "opts": self.model._meta,
                "title": "Token balansını dəyiş",
            },
        )
