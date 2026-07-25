"""Downloads real, professional real-estate-style stock photos from Pexels
for demo seed data, so listings look like a real property marketplace instead of
using illustrated placeholders.
"""

import os
from io import BytesIO

import environ
import requests
from PIL import Image

BASE_DIR_ENV = environ.Env()
_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(_ENV_PATH):
    environ.Env.read_env(_ENV_PATH)

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

TARGET_SIZE = (1200, 900)

SEARCH_QUERIES = {
    "menzil": [
        "modern apartment living room",
        "apartment interior",
        "modern kitchen interior",
        "apartment bedroom",
        "modern bathroom interior",
    ],
    "ev-villa": [
        "modern house exterior",
        "luxury villa exterior",
        "house facade",
        "villa pool garden",
        "house living room interior",
    ],
    "torpaq": [
        "empty land plot",
        "green field land",
        "countryside land aerial",
        "vacant plot for sale",
    ],
    "kommersiya": [
        "office building exterior",
        "modern office interior",
        "retail store interior",
        "warehouse interior",
        "commercial building facade",
    ],
}

_ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png")


def _search_pexels(query, limit):
    if not PEXELS_API_KEY:
        return []
    params = {
        "query": query,
        "per_page": limit,
        "orientation": "landscape",
    }
    try:
        response = requests.get(
            PEXELS_SEARCH_URL,
            params=params,
            headers={"Authorization": PEXELS_API_KEY},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return []

    urls = []
    for photo in data.get("photos", []):
        src = photo.get("src", {})
        url = src.get("large2x") or src.get("large") or src.get("original")
        if url:
            urls.append(url)
    return urls


def _download_and_normalize(url):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image.load()
    except Exception:
        return None

    if image.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
        image = background
    else:
        image = image.convert("RGB")

    target_w, target_h = TARGET_SIZE
    target_ratio = target_w / target_h
    width, height = image.size
    current_ratio = width / height
    if current_ratio > target_ratio:
        new_width = round(height * target_ratio)
        left = (width - new_width) // 2
        box = (left, 0, left + new_width, height)
    else:
        new_height = round(width / target_ratio)
        top = (height - new_height) // 2
        box = (0, top, width, top + new_height)

    image = image.crop(box).resize(TARGET_SIZE, Image.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()


def fetch_photo_pool(category_slug, per_query=12):
    """Return a list of normalized JPEG bytes for the given category slug."""
    queries = SEARCH_QUERIES.get(category_slug, ["real estate"])
    urls = []
    for query in queries:
        urls.extend(_search_pexels(query, per_query))

    pool = []
    for url in urls:
        photo_bytes = _download_and_normalize(url)
        if photo_bytes:
            pool.append(photo_bytes)
    return pool
