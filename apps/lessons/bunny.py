# apps/lessons/bunny.py

import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings


def create_bunny_video(title):
    url = f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}/videos"

    headers = {
        "AccessKey": settings.BUNNY_STREAM_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "title": title
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        return response.json().get("guid")
    else:
        raise Exception(f"Bunny Stream Error: {response.text}")


def generate_signed_video_url(video_id, user_id, expiration_minutes=10):
    """
    Secure signed playback URL tied to specific user
    """

    if not video_id:
        return None

    expiration = int(
        (datetime.utcnow() + timedelta(minutes=expiration_minutes)).timestamp()
    )

    library_id = settings.BUNNY_STREAM_LIBRARY_ID
    api_key = settings.BUNNY_STREAM_API_KEY

    base_url = f"https://iframe.mediadelivery.net/embed/{library_id}/{video_id}"

    # نربط التوقيع بالمستخدم
    string_to_sign = f"{library_id}{video_id}{expiration}{user_id}".encode("utf-8")

    signature = hmac.new(
        api_key.encode("utf-8"),
        string_to_sign,
        hashlib.sha256
    ).hexdigest()

    return f"{base_url}?expires={expiration}&signature={signature}&user={user_id}"
