from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone_number = models.CharField(max_length=30, blank=True)
    is_agent = models.BooleanField(default=False)
    agency_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    token_balance = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillər"

    def __str__(self):
        return f"{self.user.username} profili"
