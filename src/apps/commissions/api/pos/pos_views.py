from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsPosAgent

from apps.commissions.api.app.views import AppEffectiveCommissionAPIView


class PosEffectiveCommissionAPIView(AppEffectiveCommissionAPIView):
    permission_classes = [IsAuthenticated, IsPosAgent]


__all__ = ["PosEffectiveCommissionAPIView"]
