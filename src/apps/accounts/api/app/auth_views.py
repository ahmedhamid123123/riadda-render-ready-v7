from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.api.utils import api_response


class AgentLoginAPIView(APIView):
    """
    Agent Login API (JWT)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()

        if not username or not password:
            return api_response(
                "INVALID_INPUT",
                "يرجى إدخال اسم المستخدم وكلمة المرور",
                status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user or user.role != "AGENT" or not user.is_active:
            return api_response(
                "INVALID_CREDENTIALS",
                "بيانات الدخول غير صحيحة أو الحساب موقوف",
                status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return api_response(
            "SUCCESS",
            "تم تسجيل الدخول بنجاح",
            status.HTTP_200_OK,
            data={
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "agent": {
                    "id": user.id,
                    "username": user.username,
                }
            }
        )


class AdminLoginAPIView(APIView):
    """Admin/SuperAdmin Login API (JWT)."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()

        if not username or not password:
            return api_response(
                "INVALID_INPUT",
                "يرجى إدخال اسم المستخدم وكلمة المرور",
                status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user or user.role not in ("ADMIN",) or not user.is_active:
            return api_response(
                "INVALID_CREDENTIALS",
                "بيانات الدخول غير صحيحة أو الحساب موقوف",
                status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return api_response(
            "SUCCESS",
            "تم تسجيل الدخول",
            status.HTTP_200_OK,
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "is_super_admin": bool(getattr(user, "is_super_admin", False)),
                },
            },
        )
