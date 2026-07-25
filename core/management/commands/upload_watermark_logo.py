import os

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Uploads the site logo to Cloudinary under a fixed public_id so it can be "
        "fetched at request time and stamped onto listing photos as a watermark."
    )

    def add_arguments(self, parser):
        parser.add_argument("image_path", help="Path to the logo PNG file to upload")

    def handle(self, *args, **options):
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
        api_key = os.environ.get("CLOUDINARY_API_KEY")
        api_secret = os.environ.get("CLOUDINARY_API_SECRET")
        if not (cloud_name and api_key and api_secret):
            raise CommandError(
                "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET "
                "must be set (e.g. in .env) before uploading the watermark logo."
            )

        cloudinary.config(
            cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True
        )
        result = cloudinary.uploader.upload(
            options["image_path"],
            public_id=settings.WATERMARK_LOGO_PUBLIC_ID,
            overwrite=True,
            invalidate=True,
            resource_type="image",
        )
        self.stdout.write(self.style.SUCCESS(f"Uploaded: {result['secure_url']}"))
