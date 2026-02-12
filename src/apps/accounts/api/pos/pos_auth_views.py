from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.api.utils import api_response
from apps.accounts.models import User


class PosAgentLoginAPIView(APIView):
    """
    POS Agent Login API (JWT)
    Enforces POS headers and binds agent to device on first login.

    Required headers:
      - X-CLIENT: POS
      - X-DEVICE-ID: <device identifier>
    """
    permission_classes = [AllowAny]

    def post(self, request):
        if request.headers.get("X-CLIENT") != "POS":
            return api_response(
                "FORBIDDEN",
                "هذا المسار مخصص لجهاز الـ POS فقط",
                status.HTTP_403_FORBIDDEN
            )

        device_id = (request.headers.get("X-DEVICE-ID") or "").strip()
        if not device_id:
            return api_response(
                "INVALID_INPUT",
                "يرجى إرسال X-DEVICE-ID من جهاز الـ POS",
                status.HTTP_400_BAD_REQUEST
            )

        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()

        if not username or not password:
            return api_response(
                "INVALID_INPUT",
                "يرجى إدخال اسم المستخدم وكلمة المرور",
                status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user or getattr(user, "role", None) != "AGENT" or not user.is_active:
            return api_response(
                "INVALID_CREDENTIALS",
                "بيانات الدخول غير صحيحة أو الحساب موقوف",
                status.HTTP_401_UNAUTHORIZED
            )

        # Device binding: if device already bound, enforce match
        if user.pos_device_id and user.pos_device_id != device_id:
            return api_response(
                "DEVICE_MISMATCH",
                "هذا الحساب مربوط بجهاز POS آخر",
                status.HTTP_403_FORBIDDEN
            )

        # Bind on first login
        if not user.pos_device_id:
            user.pos_device_id = device_id
            user.save(update_fields=["pos_device_id"])

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
                    "pos_device_id": user.pos_device_id,
                }
            }
        )
