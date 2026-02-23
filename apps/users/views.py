from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, UserSerializer


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

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class MeView(APIView):
    """
    يرجع بيانات المستخدم الحالي بناءً على التوكن
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
