from django.urls import path

from apps.commissions.api.pos.pos_views import PosEffectiveCommissionAPIView

urlpatterns = [
    path("effective/", PosEffectiveCommissionAPIView.as_view(), name="pos-commissions-effective"),
]
