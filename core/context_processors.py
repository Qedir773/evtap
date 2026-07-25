from django.conf import settings

from listings.models import Category


def site_context(request):
    return {
        "site_name": settings.SITE_NAME,
        "nav_categories": Category.objects.all(),
    }
