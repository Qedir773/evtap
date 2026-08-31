import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.management.commands.seed_showcase import CATEGORY_DATA, PHOTOS, PLACES
from listings.models import Category, Listing, ListingImage


class Command(BaseCommand):
    help = "Mövcud vitrin istifadəçilərinə 100000–300000 AZN aralığında 30 əlavə satış elanı yaradır."

    def handle(self, *args, **options):
        random.seed(20260831)
        users = list(User.objects.filter(username__startswith="showcase_").order_by("username"))
        if len(users) < 10:
            raise CommandError("Əvvəlcə seed_showcase əmrini işə salın.")

        categories = {item.slug: item for item in Category.objects.all()}
        slugs = ["menzil", "ev-villa", "torpaq", "kommersiya"]
        now = timezone.now()
        start_number = Listing.objects.filter(owner__username__startswith="showcase_").count() + 1

        for offset in range(30):
            number = start_number + offset
            category_slug = slugs[offset % len(slugs)]
            category = categories[category_slug]
            config = CATEGORY_DATA[category_slug]
            region, district, address = PLACES[(offset + 3) % len(PLACES)]
            area = Decimal(str(round(random.uniform(*config["areas"]), 1)))
            rooms = random.randint(*config["rooms"]) if config["rooms"] else None
            floor = random.randint(2, 16) if category_slug == "menzil" else None
            total_floors = floor + random.randint(1, 4) if floor else None
            # Qiymətlər tam minliklərlə: 100000, 105000, ... 300000.
            price = random.randrange(100000, 300001, 5000)

            title = f'{config["titles"][offset % 3]} — {district} #{number}'
            room_text = f"{rooms} otaqlı, " if rooms else ""
            floor_text = f"Binanın {floor}/{total_floors}-ci mərtəbəsində yerləşir. " if floor else ""
            description = (
                f"{address} ünvanında yerləşən {room_text}{area} m² sahəli satış əmlakı təqdim olunur. "
                f"{floor_text}Obyekt keyfiyyətli materiallarla təmir edilib və istifadəyə tam hazırdır. "
                "Qaz, su, elektrik və sürətli internet xətləri mövcuddur. İstilik sistemi, kondisioner, "
                "təhlükəsizlik və parkinq imkanları təmin edilib. Ərazi nəqliyyat, məktəb, bağça, market, "
                "aptek və istirahət məkanlarına yaxındır. Sənədlər tam qaydasındadır və alqı-satqıya hazırdır. "
                "Real alıcı ilə yerində baxış zamanı qiymət müzakirə oluna bilər."
            )

            listing = Listing.objects.create(
                owner=users[offset % 10],
                category=category,
                title=title,
                description=description,
                transaction_type=Listing.TransactionType.SALE,
                price=price,
                currency=Listing.Currency.AZN,
                region=region,
                district=district,
                address_detail=address,
                rooms=rooms,
                area_m2=area,
                floor=floor,
                total_floors=total_floors,
                status=Listing.Status.APPROVED,
                views_count=random.randint(80, 3500),
                is_vip=offset < 6,
                vip_expires_at=now + timedelta(days=30) if offset < 6 else None,
                is_urgent=offset in (4, 9, 14, 19, 24, 29),
                urgent_expires_at=now + timedelta(days=14) if offset in (4, 9, 14, 19, 24, 29) else None,
                last_bumped_at=now - timedelta(hours=offset + 1),
            )

            photos = PHOTOS[category_slug]
            for order in range(4):
                ListingImage.objects.create(
                    listing=listing,
                    external_url=photos[(offset + order) % len(photos)],
                    is_cover=(order == 0),
                    order=order,
                )

        self.stdout.write(self.style.SUCCESS("30 əlavə elan yaradıldı; bütün qiymətlər 100000–300000 AZN aralığındadır."))
