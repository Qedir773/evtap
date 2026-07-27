from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import Profile

from .models import PromoCode, PromotionPricing, TokenTransaction

VIP_DURATIONS = {
    PromotionPricing.ServiceType.VIP_7: 7,
    PromotionPricing.ServiceType.VIP_10: 10,
    PromotionPricing.ServiceType.VIP_30: 30,
}
URGENT_DURATION_DAYS = 7


class InsufficientBalanceError(Exception):
    pass


class PromoCodeError(Exception):
    pass


def _get_price(service_type):
    try:
        return PromotionPricing.objects.get(service_type=service_type).token_cost
    except PromotionPricing.DoesNotExist:
        raise ValueError(f"'{service_type}' üçün qiymət konfiqurasiya olunmayıb")


@transaction.atomic
def spend_tokens(user, amount, transaction_type, description=""):
    profile = Profile.objects.select_for_update().get(user=user)
    if profile.token_balance < amount:
        raise InsufficientBalanceError("Balansınız kifayət etmir.")
    profile.token_balance -= amount
    profile.save(update_fields=["token_balance"])
    TokenTransaction.objects.create(
        user=user,
        amount=-amount,
        transaction_type=transaction_type,
        description=description,
    )
    return profile.token_balance


@transaction.atomic
def add_tokens(user, amount, transaction_type, description=""):
    profile = Profile.objects.select_for_update().get(user=user)
    profile.token_balance += amount
    profile.save(update_fields=["token_balance"])
    TokenTransaction.objects.create(
        user=user,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
    )
    return profile.token_balance


@transaction.atomic
def redeem_promocode(user, code):
    try:
        promo = PromoCode.objects.select_for_update().get(code__iexact=code)
    except PromoCode.DoesNotExist:
        raise PromoCodeError("Promokod tapılmadı.")
    if not promo.is_active:
        raise PromoCodeError("Bu promokod aktiv deyil.")
    if promo.valid_until and promo.valid_until < timezone.now():
        raise PromoCodeError("Bu promokodun müddəti bitib.")
    if promo.is_exhausted:
        raise PromoCodeError("Bu promokodun istifadə limiti bitib.")

    promo.current_uses += 1
    promo.save(update_fields=["current_uses"])
    add_tokens(
        user,
        promo.token_amount,
        TokenTransaction.Type.REDEEM,
        description=f"Promokod: {promo.code}",
    )
    return promo.token_amount


@transaction.atomic
def bump_listing(user, listing):
    if listing.owner_id != user.id:
        raise PermissionError("Bu elan sizə aid deyil.")
    cost = _get_price(PromotionPricing.ServiceType.BUMP)
    spend_tokens(user, cost, TokenTransaction.Type.SPEND, description="İrəli çəkmə")
    listing.last_bumped_at = timezone.now()
    listing.save(update_fields=["last_bumped_at"])
    return listing


@transaction.atomic
def activate_vip(user, listing, service_type):
    if listing.owner_id != user.id:
        raise PermissionError("Bu elan sizə aid deyil.")
    if service_type not in VIP_DURATIONS:
        raise ValueError("Yanlış VIP planı.")
    days = VIP_DURATIONS[service_type]
    cost = _get_price(service_type)
    spend_tokens(user, cost, TokenTransaction.Type.SPEND, description=f"VIP — {days} gün")
    now = timezone.now()
    base = listing.vip_expires_at if listing.is_currently_vip else now
    listing.is_vip = True
    listing.vip_expires_at = base + timedelta(days=days)
    listing.save(update_fields=["is_vip", "vip_expires_at"])
    return listing


@transaction.atomic
def activate_urgent(user, listing):
    if listing.owner_id != user.id:
        raise PermissionError("Bu elan sizə aid deyil.")
    cost = _get_price(PromotionPricing.ServiceType.URGENT_7)
    spend_tokens(user, cost, TokenTransaction.Type.SPEND, description=f"Təcili — {URGENT_DURATION_DAYS} gün")
    now = timezone.now()
    base = listing.urgent_expires_at if listing.is_currently_urgent else now
    listing.is_urgent = True
    listing.urgent_expires_at = base + timedelta(days=URGENT_DURATION_DAYS)
    listing.save(update_fields=["is_urgent", "urgent_expires_at"])
    return listing
