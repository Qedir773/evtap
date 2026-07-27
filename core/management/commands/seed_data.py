import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from core.placeholder_images import generate_placeholder_photo
from core.real_estate_photos import fetch_photo_pool
from listings.models import Category, Listing, ListingImage

ROOM_LABELS_BY_CATEGORY = {
    "menzil": ["Salon", "Mətbəx", "Yataq otağı", "Eyvan", "Hamam otağı"],
    "ev-villa": ["Fasad", "Bağça", "Salon", "Hovuz", "Qonaq otağı"],
    "torpaq": ["Ümumi görünüş", "Yol tərəfi", "Sahənin küncü"],
    "kommersiya": ["Giriş", "Zal", "Anbar hissəsi", "Fasad"],
}

FIRST_NAMES = [
    "Elvin", "Aysel", "Tural", "Günel", "Rəşad", "Nərmin", "Vüqar", "Səbinə",
    "Orxan", "Leyla", "Kamran", "Nigar", "Elşən", "Türkan", "Ramin", "Sevinc",
    "Anar", "Ülviyyə", "Fərid", "Aygün",
]
LAST_NAMES = [
    "Məmmədov", "Hüseynova", "Əliyev", "Qasımova", "İsmayılov", "Rzayeva",
    "Quliyev", "Abbasova", "Nağıyev", "Cəfərova", "Əhmədov", "Kərimova",
    "Bayramov", "Sadıqova", "Hacıyev", "Vəliyeva", "Muradov", "Şirinova",
]

DISTRICTS = ["Nəsimi", "Yasamal", "Xətai", "Nərimanov", "Binəqədi", "Səbail", "Nizami"]
REGIONS = ["Bakı", "Sumqayıt", "Gəncə", "Xırdalan"]

DESCRIPTION_TEMPLATES = [
    "Təmirli, günəşli, {rooms} otaqlı mənzil {district} rayonunda satılır.",
    "Mərkəzi yerləşən, metroya yaxın {area} m² sahəsi olan əmlak.",
    "Yeni tikili binada, hər cür şəraiti olan geniş sahə.",
    "Sakit küçədə yerləşən, ailə üçün əlverişli əmlak.",
    "İnvestisiya üçün əlverişli, yaxşı infrastrukturu olan ərazidə yerləşir.",
]

PRICE_RANGES = {
    ("menzil", "satis"): (60000, 350000),
    ("menzil", "kiraye"): (300, 2000),
    ("ev-villa", "satis"): (150000, 800000),
    ("ev-villa", "kiraye"): (800, 4000),
    ("torpaq", "satis"): (20000, 200000),
    ("torpaq", "kiraye"): (200, 1500),
    ("kommersiya", "satis"): (100000, 900000),
    ("kommersiya", "kiraye"): (1000, 6000),
}


class Command(BaseCommand):
    help = "EvTap üçün tamamilə kurgusal nümayiş (demo) elan və istifadəçi verisi yaradır."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=50)
        parser.add_argument("--users", type=int, default=40)
        parser.add_argument("--flush", action="store_true")

    def handle(self, *args, **options):
        count = options["count"]

        if options["flush"]:
            demo_listings = Listing.objects.filter(owner__username__startswith="demo_")
            ListingImage.objects.filter(listing__in=demo_listings).delete()
            demo_listings.delete()
            User.objects.filter(username__startswith="demo_").delete()
            self.stdout.write(
                self.style.WARNING(
                    "Mövcud demo (demo_*) elan/istifadəçi verisi silindi (digər elanlara toxunulmadı)."
                )
            )

        if not Category.objects.exists():
            call_command("loaddata", "initial_categories")
            self.stdout.write(self.style.SUCCESS("Kateqoriyalar yükləndi."))

        categories = list(Category.objects.all())

        self.stdout.write("İnternetdən əmlak fotoları yüklənir (Pexels)...")
        photo_pools = {}
        for category in categories:
            pool = fetch_photo_pool(category.slug)
            photo_pools[category.slug] = pool
            self.stdout.write(f"  {category.name}: {len(pool)} foto tapıldı.")

        users = list(User.objects.filter(username__startswith="demo_"))
        if not users:
            for i in range(options["users"]):
                first = FIRST_NAMES[i % len(FIRST_NAMES)]
                last = LAST_NAMES[i % len(LAST_NAMES)]
                username = f"demo_{first.lower()}{i}"
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="demo12345",
                    first_name=first,
                    last_name=last,
                )
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        "phone_number": f"+994 50 {random.randint(1000000, 9999999)}",
                        "is_agent": i % 3 == 0,
                        "agency_name": "EvTap Əmlak" if i % 3 == 0 else "",
                    },
                )
                users.append(user)
            self.stdout.write(self.style.SUCCESS(f"{len(users)} demo istifadəçi yaradıldı (parol: demo12345)."))

        created = 0
        for i in range(count):
            category = random.choice(categories)
            transaction_type = random.choice(list(Listing.TransactionType.values))
            price_min, price_max = PRICE_RANGES.get(
                (category.slug, transaction_type), (10000, 100000)
            )
            price = round(random.uniform(price_min, price_max), 0)

            district = random.choice(DISTRICTS)
            region = "Bakı" if random.random() < 0.7 else random.choice(REGIONS)
            rooms = random.randint(1, 5) if category.slug in ("menzil", "ev-villa") else None
            area = round(random.uniform(35, 350), 1)
            floor = random.randint(1, 16) if category.slug == "menzil" else None
            total_floors = floor + random.randint(0, 5) if floor else None

            description = random.choice(DESCRIPTION_TEMPLATES).format(
                rooms=rooms or "-", district=district, area=area
            )
            title = f"{category.name} - {district}, {rooms or ''} otaqlı".strip()

            status_roll = random.random()
            if status_roll < 0.8:
                status = Listing.Status.APPROVED
            elif status_roll < 0.9:
                status = Listing.Status.PENDING
            else:
                status = Listing.Status.REJECTED

            listing = Listing.objects.create(
                owner=random.choice(users),
                category=category,
                title=title,
                description=description,
                transaction_type=transaction_type,
                price=price,
                region=region,
                district=district,
                rooms=rooms,
                area_m2=area,
                floor=floor,
                total_floors=total_floors,
                status=status,
                rejection_reason="Şəkillər aydın deyil." if status == Listing.Status.REJECTED else "",
            )

            labels = ROOM_LABELS_BY_CATEGORY[category.slug]
            pool = photo_pools.get(category.slug) or []
            image_count = random.randint(3, 7)
            chosen_photos = (
                random.sample(pool, min(image_count, len(pool))) if pool else []
            )
            for img_index in range(image_count):
                listing_image = ListingImage(
                    listing=listing, is_cover=(img_index == 0), order=img_index
                )
                if img_index < len(chosen_photos):
                    content = ContentFile(chosen_photos[img_index])
                else:
                    label = labels[img_index % len(labels)]
                    content = generate_placeholder_photo(label, img_index + listing.pk)
                listing_image.image.save(
                    f"seed_{listing.pk}_{img_index}.jpg", content, save=True
                )

            if status == Listing.Status.APPROVED and random.random() < 0.1:
                vip_days = random.choice([7, 10, 30])
                listing.is_vip = True
                listing.vip_expires_at = timezone.now() + timedelta(days=vip_days)
                listing.save(update_fields=["is_vip", "vip_expires_at"])

            created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} kurgusal elan yaradıldı."))
