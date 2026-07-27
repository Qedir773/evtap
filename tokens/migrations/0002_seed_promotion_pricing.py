from django.db import migrations

DEFAULT_PRICES = {
    "bump": 2,
    "vip_7": 10,
    "vip_10": 14,
    "vip_30": 35,
    "urgent_7": 5,
}


def seed_pricing(apps, schema_editor):
    PromotionPricing = apps.get_model("tokens", "PromotionPricing")
    for service_type, token_cost in DEFAULT_PRICES.items():
        PromotionPricing.objects.get_or_create(
            service_type=service_type, defaults={"token_cost": token_cost}
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("tokens", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_pricing, noop),
    ]
