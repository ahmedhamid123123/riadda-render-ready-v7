from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from apps.sales.models import TelecomCompany
from apps.accounts.permissions import IsAgent
from apps.core.api.utils import api_response
from apps.core.api.messages import MESSAGES


# ============================================================
# 1️⃣ Public Catalog API
# (يعرض الشركات + المنتجات بدون أسعار)
# يستخدمه: الصفحة العامة / عرض مبدئي
# ============================================================
class PublicCatalogAPIView(APIView):
    """
    Public Catalog API
    Company -> Product Type -> Denominations
    """
    permission_classes = [AllowAny]

    def get(self, request):
        companies = (
            TelecomCompany.objects
            .filter(is_active=True)
            .prefetch_related("denominations")
            .order_by("display_order", "name_ar")
        )

        result = []

        for company in companies:
            products = {}

            for d in company.denominations.all():
                if not d.is_active:
                    continue

                products.setdefault(d.product_type, []).append({
                    "id": d.id,
                    "value": d.value
                })

            if not products:
                continue

            result.append({
                "company_id": company.id,
                "company_code": company.code,
                "company_name": company.name_ar,
                "company_type": company.company_type,
                "logo": (
                    request.build_absolute_uri(company.logo.url)
                    if company.logo else None
                ),
                "products": products
            })

        return api_response(
            "SUCCESS",
            MESSAGES.get("SUCCESS", "تم بنجاح"),
            status.HTTP_200_OK,
            data=result
        )


# ============================================================
# 2️⃣ Agent Catalog API
# (يعرض الشركات + الفئات + السعر للوكيل)
# يستخدمه: POS / Web Agent
# ============================================================
class AgentCatalogAPIView(APIView):
    """
    Agent Catalog API
    Company -> Active Denominations (with price)
    """
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        companies = (
            TelecomCompany.objects
            .filter(is_active=True)
            .prefetch_related("denominations")
            .order_by("display_order", "name_ar")
        )

        result = []

        for company in companies:
            denominations = []

            for d in company.denominations.all():
                if not d.is_active:
                    continue

                denominations.append({
                    "id": d.id,
                    "value": d.value,
                    "price_to_agent": str(d.price_to_agent),
                    "product_type": d.product_type
                })

            if not denominations:
                continue

            result.append({
                "company_id": company.id,
                "company_code": company.code,
                "company_name": company.name_ar,
                "company_type": company.company_type,
                "logo": (
                    request.build_absolute_uri(company.logo.url)
                    if company.logo else None
                ),
                "denominations": denominations
            })

        return api_response(
            "SUCCESS",
            MESSAGES.get("SUCCESS", "تم بنجاح"),
            status.HTTP_200_OK,
            data=result
        )
