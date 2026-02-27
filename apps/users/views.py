from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(APIView):
    """
    تسجيل مستخدم جديد (Teacher أو Student)
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        data = UserSerializer(user).data
        data.update({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
        return Response(data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """
    يرجع بيانات المستخدم الحالي بناءً على التوكن
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class AvatarUploadView(APIView):
    """
    رفع/تحديث صورة البروفايل للمستخدم الحالي
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('avatar') or request.FILES.get('image')
        if not file:
            return Response({"detail": "الملف avatar مطلوب."}, status=400)
        user = request.user
        user.image = file
        user.save(update_fields=['image'])
        return Response({"image_url": user.image.url if user.image else None})
