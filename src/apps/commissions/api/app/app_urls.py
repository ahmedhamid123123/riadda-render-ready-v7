from django.urls import path

from .views import AppEffectiveCommissionAPIView

urlpatterns = [
    path("effective/", AppEffectiveCommissionAPIView.as_view(), name="app-commissions-effective"),
]
