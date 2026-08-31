import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from listings.models import Category, Listing, ListingImage


PEOPLE = [
    ("Elvin", "Məmmədov"), ("Aysel", "Hüseynova"), ("Tural", "Əliyev"),
    ("Günel", "Qasımova"), ("Rəşad", "İsmayılov"), ("Nərmin", "Rzayeva"),
    ("Vüqar", "Quliyev"), ("Səbinə", "Abbasova"), ("Orxan", "Nağıyev"),
    ("Leyla", "Cəfərova"),
]

PLACES = [
    ("Bakı", "Nəsimi", "28 May metrosu, Səməd Vurğun küçəsi"),
    ("Bakı", "Yasamal", "Elmlər Akademiyası metrosu, Hüseyn Cavid prospekti"),
    ("Bakı", "Xətai", "Xətai metrosu, Ağ Şəhər yaşayış kompleksi"),
    ("Bakı", "Nərimanov", "Gənclik metrosu, Təbriz küçəsi"),
    ("Bakı", "Səbail", "İçərişəhər metrosu, Badamdar qəsəbəsi"),
    ("Bakı", "Binəqədi", "Azadlıq prospekti metrosu, 8-ci mikrorayon"),
    ("Bakı", "Nizami", "Neftçilər metrosu, Qara Qarayev prospekti"),
    ("Xırdalan", "Abşeron", "Heydər Əliyev prospekti, Kristal Abşeron"),
    ("Sumqayıt", "Sumqayıt", "Bulvar ərazisi, Sülh küçəsi"),
    ("Gəncə", "Kəpəz", "Atatürk prospekti, şəhər mərkəzi"),
]

PHOTOS = {
    "menzil": [
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600585152915-d208bec867a1?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1400&q=85",
    ],
    "ev-villa": [
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600566753051-f0b89df2dd90?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1600566752355-35792bedcfea?auto=format&fit=crop&w=1400&q=85",
    ],
    "torpaq": [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1400&q=85",
    ],
    "kommersiya": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1400&q=85",
        "https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?auto=format&fit=crop&w=1400&q=85",
    ],
}

CATEGORY_DATA = {
    "menzil": {
        "titles": ["Yeni tikilidə geniş və işıqlı mənzil", "Metroya yaxın premium təmirli mənzil", "Şəhər mənzərəli ailə mənzili"],
        "areas": (55, 185), "rooms": (2, 5), "prices": (95000, 420000),
    },
    "ev-villa": {
        "titles": ["Hovuzlu və geniş bağçalı villa", "Dəniz mənzərəli fərdi yaşayış evi", "Sakit ərazidə modern bağ evi"],
        "areas": (160, 520), "rooms": (4, 8), "prices": (220000, 950000),
    },
    "torpaq": {
        "titles": ["Tikinti üçün əlverişli torpaq sahəsi", "Sənədli və kommunikasiya xətləri yaxın torpaq", "İnvestisiya üçün perspektivli torpaq"],
        "areas": (300, 2400), "rooms": None, "prices": (35000, 280000),
    },
    "kommersiya": {
        "titles": ["İşlək ərazidə hazır kommersiya obyekti", "Biznes mərkəzində müasir ofis", "Vitrinli və geniş ticarət sahəsi"],
        "areas": (70, 600), "rooms": None, "prices": (140000, 850000),
    },
}


class Command(BaseCommand):
    help = "10 istifadəçi və 30 dolğun, real fotolu nümayiş elanı yaradır."

    def handle(self, *args, **options):
        random.seed(773)

        old = Listing.objects.filter(owner__username__startswith="showcase_")
        ListingImage.objects.filter(listing__in=old).delete()
        old.delete()
        User.objects.filter(username__startswith="showcase_").delete()

        # Əvvəlki boş demo verilərini də təmizlə, real hesab və elanlara toxunma.
        old_demo = Listing.objects.filter(owner__username__startswith="demo_")
        ListingImage.objects.filter(listing__in=old_demo).delete()
        old_demo.delete()
        User.objects.filter(username__startswith="demo_").delete()

        if not Category.objects.exists():
            call_command("loaddata", "initial_categories")
        categories = {item.slug: item for item in Category.objects.all()}

        users = []
        for index, (first, last) in enumerate(PEOPLE, 1):
            username = f"showcase_user_{index:02d}"
            user = User.objects.create_user(
                username=username,
                email=f"{username}@evtap.az",
                password="EvTapDemo2026!",
                first_name=first,
                last_name=last,
            )
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "phone_number": f"+994 50 {330 + index:03d} {20 + index:02d} {30 + index:02d}",
                    "is_agent": index in (1, 3, 6, 8),
                    "agency_name": "EvTap Premium Əmlak" if index in (1, 3, 6, 8) else "",
                },
            )
            users.append(user)

        slugs = ["menzil", "ev-villa", "torpaq", "kommersiya"]
        now = timezone.now()
        for index in range(30):
            category_slug = slugs[index % len(slugs)]
            category = categories[category_slug]
            config = CATEGORY_DATA[category_slug]
            region, district, address = PLACES[index % len(PLACES)]
            transaction = "kiraye" if index % 5 == 0 else "satis"
            area = Decimal(str(round(random.uniform(*config["areas"]), 1)))
            rooms = random.randint(*config["rooms"]) if config["rooms"] else None
            floor = random.randint(2, 15) if category_slug == "menzil" else None
            total_floors = floor + random.randint(1, 5) if floor else None
            low, high = config["prices"]
            price = random.randint(low, high)
            if transaction == "kiraye":
                price = random.randint(650, 4500)

            title = f'{config["titles"][index % 3]} — {district}'
            room_text = f"{rooms} otaqlı, " if rooms else ""
            floor_text = f"{floor}/{total_floors} mərtəbədə yerləşir. " if floor else ""
            description = (
                f"{address} ünvanında yerləşən {room_text}{area} m² sahəli əmlak təqdim olunur. "
                f"{floor_text}Əmlak tam təmirlidir, işıqlı və funksional planlanmaya malikdir. "
                "Qaz, su və elektrik daimidir; sürətli internet, istilik sistemi və kondisioner mövcuddur. "
                "Yaxınlıqda məktəb, uşaq bağçası, supermarket, ictimai nəqliyyat dayanacağı və istirahət zonası var. "
                "Sənədlər qaydasındadır. Real alıcı və ya uzunmüddətli kirayəçi ilə qiymətdə razılaşmaq mümkündür. "
                "Baxış keçirmək üçün əvvəlcədən əlaqə saxlamağınız xahiş olunur."
            )

            listing = Listing.objects.create(
                owner=users[index % len(users)],
                category=category,
                title=title,
                description=description,
                transaction_type=transaction,
                price=price,
                currency="AZN",
                region=region,
                district=district,
                address_detail=address,
                rooms=rooms,
                area_m2=area,
                floor=floor,
                total_floors=total_floors,
                status=Listing.Status.APPROVED,
                views_count=random.randint(45, 2800),
                is_vip=index < 8,
                vip_expires_at=now + timedelta(days=30) if index < 8 else None,
                is_urgent=index in (2, 7, 12, 17, 22),
                urgent_expires_at=now + timedelta(days=14) if index in (2, 7, 12, 17, 22) else None,
                last_bumped_at=now - timedelta(hours=index * 3),
            )

            gallery = PHOTOS[category_slug]
            start = index % len(gallery)
            selected = [gallery[(start + offset) % len(gallery)] for offset in range(4)]
            for order, url in enumerate(selected):
                ListingImage.objects.create(
                    listing=listing,
                    external_url=url,
                    is_cover=(order == 0),
                    order=order,
                )

        self.stdout.write(self.style.SUCCESS("10 istifadəçi, 30 dolğun elan və 120 internet fotosu yaradıldı."))
