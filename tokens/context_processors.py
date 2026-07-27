from .models import PromotionPricing


def token_context(request):
    context = {
        "promotion_pricing": {p.service_type: p.token_cost for p in PromotionPricing.objects.all()},
    }
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        context["user_token_balance"] = profile.token_balance if profile else 0
    return context
