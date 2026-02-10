# apps/lessons/utils.py
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings
import os

def generate_bunny_signed_url(video_id, expiration_hours=5):
    """
    Generates a signed URL for Bunny.net Stream.
    
    أين يتم التحقق؟
    1. تأكد من أن متغيرات البيئة BUNNY_LIBRARY_ID و BUNNY_API_KEY موجودة في .env
    2. تأكد من أن video_id صحيح وليس فارغاً قبل استدعاء الدالة.
    """
    library_id = os.getenv('BUNNY_LIBRARY_ID')
    api_key = os.getenv('BUNNY_API_KEY')
    
    if not library_id or not api_key or not video_id:
        return None

    # تحديد وقت انتهاء الصلاحية
    expiration = int((datetime.utcnow() + timedelta(hours=expiration_hours)).timestamp())
    
    # بناء الرابط الأساسي
    # يمكنك تغيير الـ domain حسب إعدادات الحساب (iframe.mediadelivery.net أو custom domain)
    url = f"https://iframe.mediadelivery.net/embed/{library_id}/{video_id}"
    
    # إنشاء التوقيع (Signature)
    # الصيغة: md5(ip + expiration + api_key) أو حسب توثيق Bunny الحالي
    # هنا نستخدم الطريقة القياسية للتوقيع: hmac-sha256
    string_to_sign = f"{library_id}{video_id}{expiration}".encode('utf-8')
    
    # ملاحظة: بعض إصدارات Bunny تستخدم MD5، والبعض HMAC. سنستخدم HMAC لأمان أفضل.
    signature = hmac.new(api_key.encode('utf-8'), string_to_sign, hashlib.sha256).hexdigest()
    
    # إضافة المعاملات للرابط
    signed_url = f"{url}?expires={expiration}&signature={signature}"
    
    return signed_url