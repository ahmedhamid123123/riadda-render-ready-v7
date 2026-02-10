from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status

from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


class SystemPingAPIView(APIView):
    """
    System Ping API
    - Public
    - Used by POS to check server status
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return api_response(
            "SUCCESS",
            MESSAGES.get("OK", "OK"),
            status.HTTP_200_OK,
            data={
                "status": "ok",
                "server_time": timezone.now().isoformat()
            }
        )
