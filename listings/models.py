import json
from io import BytesIO

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, UnidentifiedImageError

LISTING_IMAGE_SIZE = (1200, 900)  # 4:3 yatay (landscape) format

WATERMARK_CACHE_KEY = "site-watermark-logo-bytes"
WATERMARK_CACHE_TIMEOUT = 3600  # saniyə
WATERMARK_WIDTH_RATIO = 0.14  # elan şəklinin enindən nisbət
# Qalereya görünüşü (16:9) 4:3 şəkli mərkəzdən kəsir (yuxarı/aşağı ~12.5%).
# Loqo bu "təhlükəsiz zona"dan kənara düşməsin deyə marginlər nisbi seçilib.
WATERMARK_MARGIN_X_RATIO = 0.03
WATERMARK_MARGIN_Y_RATIO = 0.15


def _fetch_watermark_logo_bytes():
    """Sayt logosunu Cloudinary-dən çəkir və prosesin yaddaşında keşləyir."""
    cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", None)
    if not cloud_name:
        return None

    logo_bytes = cache.get(WATERMARK_CACHE_KEY)
    if logo_bytes is not None:
        return logo_bytes

    url = (
        f"https://res.cloudinary.com/{cloud_name}/image/upload/"
        f"{settings.WATERMARK_LOGO_PUBLIC_ID}.png"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None

    logo_bytes = response.content
    cache.set(WATERMARK_CACHE_KEY, logo_bytes, WATERMARK_CACHE_TIMEOUT)
    return logo_bytes


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    icon_css_class = models.CharField(max_length=50, blank=True, default="icon-home")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Kateqoriya"
        verbose_name_plural = "Kateqoriyalar"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("listings:category_list", kwargs={"slug": self.slug})


class ListingQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(status=Listing.Status.APPROVED)

    def currently_vip(self):
        return self.approved().filter(
            is_vip=True, vip_expires_at__gte=timezone.now()
        )


class Listing(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Gözləmədə"
        APPROVED = "approved", "Təsdiqlənib"
        REJECTED = "rejected", "Rədd edilib"

    class TransactionType(models.TextChoices):
        SALE = "satis", "Satış"
        RENT = "kiraye", "Kirayə"

    class Currency(models.TextChoices):
        AZN = "AZN", "AZN"
        USD = "USD", "USD"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="listings"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices, default=TransactionType.SALE
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.AZN
    )
    region = models.CharField(max_length=100, default="Bakı")
    district = models.CharField(max_length=100, blank=True)
    address_detail = models.CharField(max_length=255, blank=True)
    rooms = models.PositiveSmallIntegerField(null=True, blank=True)
    area_m2 = models.DecimalField(max_digits=8, decimal_places=1)
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    total_floors = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    rejection_reason = models.TextField(blank=True)
    is_vip = models.BooleanField(default=False)
    vip_expires_at = models.DateTimeField(null=True, blank=True)
    is_urgent = models.BooleanField(default=False)
    urgent_expires_at = models.DateTimeField(null=True, blank=True)
    last_bumped_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ListingQuerySet.as_manager()

    class Meta:
        verbose_name = "Elan"
        verbose_name_plural = "Elanlar"
        ordering = ["-is_vip", "-is_urgent", "-last_bumped_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "category"]),
            models.Index(fields=["status", "transaction_type"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:200] or "elan"
            candidate = base_slug
            counter = 1
            while Listing.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                counter += 1
                candidate = f"{base_slug}-{counter}"
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "listings:listing_detail", kwargs={"slug": self.slug, "pk": self.pk}
        )

    @property
    def is_currently_vip(self):
        return bool(
            self.is_vip and self.vip_expires_at and self.vip_expires_at >= timezone.now()
        )

    @property
    def is_currently_urgent(self):
        return bool(
            self.is_urgent and self.urgent_expires_at and self.urgent_expires_at >= timezone.now()
        )

    @property
    def ordered_images(self):
        return list(self.images.all())

    @property
    def cover_image(self):
        images = self.ordered_images
        for img in images:
            if img.is_cover:
                return img
        return images[0] if images else None

    @property
    def gallery_urls(self):
        return [img.display_url for img in self.ordered_images if img.display_url]


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="listings/%Y/%m/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Elan Şəkli"
        verbose_name_plural = "Elan Şəkilləri"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.listing.title} - şəkil {self.pk}"

    def save(self, *args, **kwargs):
        if self.image and isinstance(self.image.file, UploadedFile):
            self._crop_to_landscape(getattr(self, "_crop_box", None))
        super().save(*args, **kwargs)

    def _crop_to_landscape(self, crop_box_json=None):
        """Yeni yüklənən şəkli sabit yatay (landscape) formata kəsir.

        İstifadəçi özü kəsmə sahəsini seçibsə (crop_box_json — nisbi x/y/width/height,
        0..1 aralığında), həmin sahə istifadə olunur; əks halda mərkəzdən avtomatik kəsilir.
        """
        self.image.open()
        image = Image.open(self.image)
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
            image = background
        else:
            image = image.convert("RGB")

        target_w, target_h = LISTING_IMAGE_SIZE
        target_ratio = target_w / target_h
        width, height = image.size
        box = self._parse_crop_box(crop_box_json, width, height)

        if box is None:
            current_ratio = width / height
            if current_ratio > target_ratio:
                new_width = round(height * target_ratio)
                left = (width - new_width) // 2
                box = (left, 0, left + new_width, height)
            else:
                new_height = round(width / target_ratio)
                top = (height - new_height) // 2
                box = (0, top, width, top + new_height)

        image = image.crop(box).resize(LISTING_IMAGE_SIZE, Image.LANCZOS)
        image = self._apply_watermark(image)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=95, subsampling=0)
        name = self.image.name.rsplit(".", 1)[0] + ".jpg"
        self.image.save(name, ContentFile(buffer.getvalue()), save=False)

    @staticmethod
    def _apply_watermark(image):
        """Sayt logosunu şəklin aşağı-sağ küncünə şəffaf watermark kimi əlavə edir."""
        logo_bytes = _fetch_watermark_logo_bytes()
        if not logo_bytes:
            return image

        try:
            logo = Image.open(BytesIO(logo_bytes)).convert("RGBA")
        except UnidentifiedImageError:
            return image

        target_width = round(image.width * WATERMARK_WIDTH_RATIO)
        target_height = round(logo.height * (target_width / logo.width))
        logo = logo.resize((target_width, target_height), Image.LANCZOS)

        margin_x = round(image.width * WATERMARK_MARGIN_X_RATIO)
        margin_y = round(image.height * WATERMARK_MARGIN_Y_RATIO)
        position = (
            image.width - target_width - margin_x,
            image.height - target_height - margin_y,
        )
        watermarked = image.convert("RGBA")
        watermarked.paste(logo, position, mask=logo)
        return watermarked.convert("RGB")

    @staticmethod
    def _parse_crop_box(crop_box_json, width, height):
        if not crop_box_json:
            return None
        try:
            data = json.loads(crop_box_json)
            x = max(0.0, min(1.0, float(data["x"])))
            y = max(0.0, min(1.0, float(data["y"])))
            w = max(0.01, min(1.0 - x, float(data["width"])))
            h = max(0.01, min(1.0 - y, float(data["height"])))
        except (TypeError, ValueError, KeyError, json.JSONDecodeError):
            return None
        left = round(x * width)
        top = round(y * height)
        right = max(left + 1, round((x + w) * width))
        bottom = max(top + 1, round((y + h) * height))
        return (left, top, min(right, width), min(bottom, height))

    @property
    def display_url(self):
        if self.image:
            return self.image.url
        if self.external_url:
            return self.external_url
        return ""


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sevimli"
        verbose_name_plural = "Sevimlilər"
        unique_together = ("user", "listing")

    def __str__(self):
        return f"{self.user} -> {self.listing}"
