from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone

from apps.core.api.utils import api_response


class SystemHealthAPIView(APIView):
    """
    System Health / Ping API
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return api_response(
            "SUCCESS",
            "النظام يعمل بشكل طبيعي",
            status.HTTP_200_OK,
            data={
                "status": "OK",
                "server_time": timezone.now().isoformat()
            }
        )
