import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from rest_framework.test import APIClient
client = APIClient()
payload = {
    "email": "http_student@example.com",
    "first_name": "Http",
    "last_name": "Student",
    "password": "HttpPass123",
    "password_confirm": "HttpPass123",
    "user_type": "student",
}
resp = client.post("/api/auth/register/", payload, format="json")
print(resp.status_code)
try:
    print(resp.data)
except Exception as e:
    print("no_data", repr(e))
