import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from listings.models import Listing

PLAN_PRICES = {
    "7": 5,
    "15": 9,
    "30": 15,
}


class Promotion(models.Model):
    class Plan(models.TextChoices):
        DAYS_7 = "7", "7 gün"
        DAYS_15 = "15", "15 gün"
        DAYS_30 = "30", "30 gün"

    class Status(models.TextChoices):
        PENDING = "pending", "Gözləmədə"
        PAID = "paid", "Ödənilib (DEMO)"
        FAILED = "failed", "Uğursuz"

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="promotions"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=2, choices=Plan.choices)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default="AZN")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    mock_reference_code = models.CharField(max_length=32, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Promosyon (Demo Ödəniş)"
        verbose_name_plural = "Promosyonlar (Demo Ödənişlər)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.listing.title} - {self.plan} gün - {self.status}"

    def save(self, *args, **kwargs):
        if not self.mock_reference_code:
            self.mock_reference_code = f"DEMO-{uuid.uuid4().hex[:12].upper()}"
        if not self.amount:
            self.amount = PLAN_PRICES.get(self.plan, 0)
        super().save(*args, **kwargs)

    def mark_paid(self):
        from datetime import timedelta

        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

        self.listing.is_featured = True
        self.listing.featured_until = timezone.now() + timedelta(days=int(self.plan))
        self.listing.save(update_fields=["is_featured", "featured_until"])
