from rest_framework import serializers
from decimal import Decimal


class AdjustBalanceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
