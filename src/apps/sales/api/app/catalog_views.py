from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.sales.models import RechargeDenomination
from apps.core.api.utils import api_response


class PublicCatalogAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = list(
            RechargeDenomination.objects.filter(is_active=True).values(
                "id", "value", "price_to_agent", "company__code", "company__name_ar"
            )
        )
        return api_response("SUCCESS", "OK", data={"items": items})


class AgentCatalogAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # For app, keep simple public list (agents are authenticated at transport layer)
        items = list(
            RechargeDenomination.objects.filter(is_active=True).values(
                "id", "value", "price_to_agent", "company__code", "company__name_ar"
            )
        )
        return api_response("SUCCESS", "OK", data={"items": items})
