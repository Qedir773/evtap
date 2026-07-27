from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile

from .models import TokenTransaction

SIGNUP_BONUS_AMOUNT = 20


@receiver(post_save, sender=Profile)
def grant_signup_bonus(sender, instance, created, **kwargs):
    if not created:
        return
    profile = instance
    profile.token_balance += SIGNUP_BONUS_AMOUNT
    profile.save(update_fields=["token_balance"])
    TokenTransaction.objects.create(
        user=profile.user,
        amount=SIGNUP_BONUS_AMOUNT,
        transaction_type=TokenTransaction.Type.BONUS,
        description="Qeydiyyat bonusu",
    )
