from django.core.management.base import BaseCommand

from listings.models import Listing, ListingImage


HOUSE_PHOTOS = [
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600585152915-d208bec867a1?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600566753051-f0b89df2dd90?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1600566752355-35792bedcfea?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1400&q=85",
]


class Command(BaseCommand):
    help = "Bütün vitrin elanlarının şəkillərini yalnız real ev, bina və interyer fotoları ilə əvəz edir."

    def handle(self, *args, **options):
        listings = Listing.objects.filter(
            owner__username__startswith="showcase_"
        ).order_by("id")

        replaced = 0
        for index, listing in enumerate(listings):
            ListingImage.objects.filter(listing=listing).delete()
            start = (index * 3) % len(HOUSE_PHOTOS)
            for order in range(4):
                ListingImage.objects.create(
                    listing=listing,
                    external_url=HOUSE_PHOTOS[(start + order) % len(HOUSE_PHOTOS)],
                    is_cover=(order == 0),
                    order=order,
                )
                replaced += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{listings.count()} elanın {replaced} şəkli real ev/bina fotoları ilə əvəz edildi."
            )
        )
