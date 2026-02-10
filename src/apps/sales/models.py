# apps.core/sales/models.py

import uuid
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone


# =====================================================
# Telecom Company
# =====================================================
class TelecomCompany(models.Model):
    """
    شركة الاتصالات (الأدمن يضيفها ويرفع اللوغو)
    """

    PRODUCT_TYPES = (
        ('MOBILE', 'Mobile'),
        ('INTERNET', 'Internet'),
    )

    code = models.CharField(max_length=30, unique=True)
    name_ar = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="companies/", null=True, blank=True)

    company_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        default='MOBILE'
    )

    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name_ar']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['company_type']),
        ]

    def __str__(self):
        return self.name_ar


# =====================================================
# Recharge Denomination
# =====================================================
class RechargeDenomination(models.Model):
    """
    فئة الشحن داخل شركة
    """

    PRODUCT_TYPES = (
        ('MOBILE', 'Mobile Recharge'),
        ('INTERNET', 'Internet Card'),
    )

    company = models.ForeignKey(
        TelecomCompany,
        on_delete=models.CASCADE,
        related_name='denominations'
    )

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES
    )

    value = models.PositiveIntegerField()

    # Pricing snapshot base
    cost_to_company = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_to_agent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_to_customer = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('company', 'product_type', 'value')
        ordering = ['company', 'value']
        indexes = [
            models.Index(fields=['product_type', 'is_active']),
            models.Index(fields=['value']),
        ]

    def __str__(self):
        return f"{self.company.name_ar} - {self.value}"


# =====================================================
# Transaction
# =====================================================
class Transaction(models.Model):
    """
    عملية البيع / التأكيد (WEB + POS)
    """

    STATUS_CHOICES = (
        ('PRINTED', 'Printed'),
        ('CONFIRMED', 'Confirmed'),
    )

    SOURCE_CHOICES = (
        ('WEB', 'Web'),
        ('POS', 'POS'),
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    company = models.ForeignKey(
        TelecomCompany,
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    denomination = models.ForeignKey(
        RechargeDenomination,
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    # كود الكارت (حساس – لاحقًا تشفير)
    code = models.CharField(max_length=150)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PRINTED',
        db_index=True
    )

    # Snapshot وقت العملية
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ===== Receipt =====
    public_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )

    receipt_expires_at = models.DateTimeField(null=True, blank=True)

    receipt_reissue_count = models.PositiveIntegerField(default=0)
    receipt_reissue_limit = models.PositiveIntegerField(default=3)

    # Snapshot of exactly what the POS printed/shown (for admin preview)
    receipt_payload = models.JSONField(null=True, blank=True)
    receipt_payload_version = models.PositiveIntegerField(default=1)

    # Tamper-evident signature for receipt_payload (HMAC over a canonical representation).
    receipt_hmac = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    receipt_hmac_algo = models.CharField(max_length=32, default='HMAC-SHA256')
    receipt_hmac_created_at = models.DateTimeField(null=True, blank=True)

    # ===== POS Metadata =====
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='WEB',
        db_index=True
    )

    device_id = models.CharField(max_length=100, null=True, blank=True)
    offline_uuid = models.UUIDField(null=True, blank=True, unique=True)

    # ===== Timestamps =====
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['agent', 'created_at']),
        ]

    def __str__(self):
        return f"{self.company.name_ar} - {self.denomination.value} - {self.status}"

    # ===== Receipt Helpers =====
    def set_receipt_expiry(self, hours: int = 24):
        base_time = self.confirmed_at or timezone.now()
        self.receipt_expires_at = base_time + timedelta(hours=int(hours))

    def is_receipt_expired(self) -> bool:
        if not self.receipt_expires_at:
            return False
        return timezone.now() > self.receipt_expires_at