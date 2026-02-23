import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from apps.users.serializers import RegisterSerializer, UserSerializer

data = {
    "email": "test_student@example.com",
    "first_name": "Test",
    "last_name": "Student",
    "password": "TestPass123",
    "password_confirm": "TestPass123",
    "user_type": "student",
}
ser = RegisterSerializer(data=data)
if ser.is_valid():
    try:
        user = ser.save()
        print(UserSerializer(user).data)
    except Exception as e:
        print("save_error:", repr(e))
else:
    print(ser.errors)
