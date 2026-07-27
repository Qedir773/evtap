from django.conf import settings
from django.db import models


class TokenTransaction(models.Model):
    class Type(models.TextChoices):
        BONUS = "bonus", "Qeydiyyat bonusu"
        SPEND = "spend", "Xərclənib"
        PURCHASE = "purchase", "Alış"
        ADMIN_ADD = "admin_add", "Admin tərəfindən əlavə"
        REDEEM = "redeem", "Promokod"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="token_transactions"
    )
    amount = models.IntegerField(help_text="Müsbət = artım, mənfi = xərclənmə")
    transaction_type = models.CharField(max_length=10, choices=Type.choices)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token Tranzaksiyası"
        verbose_name_plural = "Token Tranzaksiyaları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.amount:+d} ({self.get_transaction_type_display()})"


class PromoCode(models.Model):
    code = models.CharField(max_length=40, unique=True)
    token_amount = models.PositiveIntegerField()
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Promokod"
        verbose_name_plural = "Promokodlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_exhausted(self):
        return self.current_uses >= self.max_uses


class PromotionPricing(models.Model):
    class ServiceType(models.TextChoices):
        BUMP = "bump", "İrəli çək"
        VIP_7 = "vip_7", "VIP — 7 gün"
        VIP_10 = "vip_10", "VIP — 10 gün"
        VIP_30 = "vip_30", "VIP — 30 gün"
        URGENT_7 = "urgent_7", "Təcili — 7 gün"

    service_type = models.CharField(max_length=20, choices=ServiceType.choices, unique=True)
    token_cost = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Xidmət Qiyməti"
        verbose_name_plural = "Xidmət Qiymətləri"
        ordering = ["service_type"]

    def __str__(self):
        return f"{self.get_service_type_display()} — {self.token_cost} token"
