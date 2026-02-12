# src/apps/accounts/models.py

import uuid

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        AGENT = "AGENT", "Agent"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.AGENT,
        db_index=True,
    )

    is_super_admin = models.BooleanField(default=False, db_index=True)

    # POS device binding (Sunmi / Android)
    pos_device_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text='Bound POS device identifier (e.g., Sunmi serial/Android ID)'
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


    @property
    def permissions(self):
        """Return the related AdminPermission instance or None.

        Templates and existing code expect `request.user.permissions`.
        This property provides a convenient accessor that returns the
        OneToOne `admin_permissions` object when present, otherwise None.
        """
        try:
            return self.admin_permissions
        except Exception:
            return None

class AdminPermission(models.Model):
    """
    Matrix صلاحيات الأدمن (غير السوبر أدمن).

    ملاحظات:
    - Super Admin لا يعتمد على هذا الجدول.
    - أي Admin عادي يجب أن يكون له سجل واحد فقط هنا (OneToOne).
    """

    class Preset(models.TextChoices):
        CUSTOM = "CUSTOM", "مخصص"
        READ_ONLY = "READ_ONLY", "قراءة فقط"
        MANAGER = "MANAGER", "مدير"
        ACCOUNTANT = "ACCOUNTANT", "محاسب"

    admin = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="admin_permissions",
        limit_choices_to={"role": User.Role.ADMIN},
        help_text="يرتبط فقط بالمستخدمين من نوع ADMIN",
    )

    preset = models.CharField(
        max_length=20,
        choices=Preset.choices,
        default=Preset.CUSTOM,
        db_index=True,
    )

    # Agent permissions
    can_view_agents = models.BooleanField(default=True, help_text="عرض قائمة الوكلاء")
    can_add_agents = models.BooleanField(default=False, help_text="إضافة وكيل جديد")
    can_edit_agents = models.BooleanField(default=False, help_text="تعديل بيانات الوكلاء")

    # Commission permissions
    can_view_commissions = models.BooleanField(default=False, help_text="عرض العمولات")
    can_edit_commissions = models.BooleanField(default=False, help_text="تعديل العمولات")

    # Reports & Logs
    can_view_reports = models.BooleanField(default=False, help_text="عرض التقارير")
    # Profit visibility (can be toggled per-admin by Super Admin)
    can_view_profit = models.BooleanField(default=True, help_text="عرض صفحة الأرباح")
    can_view_audit_logs = models.BooleanField(default=False, help_text="عرض سجل العمليات")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Permission"
        verbose_name_plural = "Admin Permissions"
        indexes = [
            models.Index(fields=["preset"]),
            models.Index(fields=["updated_at"]),
        ]

    def apply_preset(self, preset_code: str) -> None:
        """
        تطبيق صلاحيات جاهزة حسب نوع المشرف.
        (ملاحظة: لا تحفظ هنا، فقط تعدّل القيم. استخدم save() خارجاً إذا تحتاج)
        """
        preset_code = (preset_code or "").strip().upper()
        if preset_code not in self.Preset.values:
            preset_code = self.Preset.CUSTOM

        self.preset = preset_code

        if preset_code == self.Preset.READ_ONLY:
            self.can_view_agents = True
            self.can_add_agents = False
            self.can_edit_agents = False

            self.can_view_commissions = True
            self.can_edit_commissions = False

            self.can_view_reports = True
            self.can_view_profit = True
            self.can_view_audit_logs = True

        elif preset_code == self.Preset.MANAGER:
            self.can_view_agents = True
            self.can_add_agents = True
            self.can_edit_agents = True

            self.can_view_commissions = True
            self.can_edit_commissions = True

            self.can_view_reports = True
            self.can_view_profit = True
            self.can_view_audit_logs = True

        elif preset_code == self.Preset.ACCOUNTANT:
            self.can_view_agents = True
            self.can_add_agents = False
            self.can_edit_agents = False

            self.can_view_commissions = True
            self.can_edit_commissions = False

            self.can_view_reports = True
            self.can_view_profit = True
            self.can_view_audit_logs = True

        # CUSTOM: لا نغيّر شيء (تعديل يدوي)

    def __str__(self) -> str:
        return f"AdminPermission({self.admin.username}) [{self.preset}]"


class AuditLog(models.Model):
    """
    سجل عمليات النظام (Admin/Agent actions)
    """

    class Action(models.TextChoices):
        # Agent actions
        SELL = "SELL", "Sell Recharge"
        CONFIRM = "CONFIRM", "Confirm Recharge"
        REISSUE_RECEIPT = "REISSUE_RECEIPT", "Reissue Receipt"

        # Admin agent management
        ADD_AGENT = "ADD_AGENT", "Add Agent"
        RESET_AGENT_PASSWORD = "RESET_AGENT_PASSWORD", "Reset Agent Password"
        SUSPEND_AGENT = "SUSPEND_AGENT", "Suspend Agent"
        ACTIVATE_AGENT = "ACTIVATE_AGENT", "Activate Agent"
        DELETE_AGENT = "DELETE_AGENT", "Delete Agent"
        ADJUST_BALANCE = "ADJUST_BALANCE", "Adjust Balance"

        # Admin commissions
        UPDATE_DEFAULT_COMMISSION = "UPDATE_DEFAULT_COMMISSION", "Update Default Commission"
        ADD_AGENT_COMMISSION = "ADD_AGENT_COMMISSION", "Add Agent Commission"

        # Admin admins management
        ADD_ADMIN = "ADD_ADMIN", "Add Admin"
        RESET_ADMIN_PASSWORD = "RESET_ADMIN_PASSWORD", "Reset Admin Password"
        DISABLE_ADMIN = "DISABLE_ADMIN", "Disable Admin"
        DELETE_ADMIN = "DELETE_ADMIN", "Delete Admin"
        TOGGLE_SUPER_ADMIN = "TOGGLE_SUPER_ADMIN", "Toggle Super Admin"
        UPDATE_ADMIN_PERMISSIONS = "UPDATE_ADMIN_PERMISSIONS", "Update Admin Permissions"
        UPDATE_AGENT_USERNAME = "UPDATE_AGENT_USERNAME", "Update Agent Username"
        TOGGLE_SHOW_PROFIT = "TOGGLE_SHOW_PROFIT", "Toggle Show Profit Setting"
        TOGGLE_ALLOW_AGENT_USERNAME_EDIT = "TOGGLE_ALLOW_AGENT_USERNAME_EDIT", "Toggle Allow Agent Username Edit"

    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_actions",
    )

    action = models.CharField(max_length=50, choices=Action.choices, db_index=True)

    target_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_targets",
    )

    transaction_id = models.UUIDField(null=True, blank=True, default=None)

    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        actor = self.actor.username if self.actor else "SYSTEM"
        return f"{self.action} by {actor}"


class SystemSetting(models.Model):
    """
    إعدادات عامة للنظام
    """

    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["key"])]

    def __str__(self) -> str:
        return self.key


# ==========================================================
# ✅ Signals: إنشاء العلاقات الناقصة تلقائياً بدون import loops
# ==========================================================

@receiver(post_save, sender=User)
def ensure_user_related_objects(sender, instance: User, created: bool, **kwargs):
    """
    Signal مسؤول عن:
    1️⃣ ترقية Django superuser إلى Super Admin داخل النظام
    2️⃣ إنشاء AdminPermission للأدمن العادي (غير السوبر)
    3️⃣ إنشاء AgentBalance تلقائيًا للوكلاء
    """

    # 1) Django superuser → Super Admin
    if instance.is_superuser and instance.role != User.Role.ADMIN:
        # تحديث بدون إعادة حفظ instance لتجنب تكرار signals
        sender.objects.filter(pk=instance.pk).update(
            role=User.Role.ADMIN,
            is_super_admin=True,
        )
        return

    # 2) Admin عادي
    if instance.role == User.Role.ADMIN and not instance.is_super_admin:
        AdminPermission.objects.get_or_create(admin=instance)

    # 3) Agent → AgentBalance (بدون import مباشر لتجنب loops)
    if instance.role == User.Role.AGENT:
        AgentBalance = apps.get_model("billing", "AgentBalance")
        if AgentBalance:
            AgentBalance.objects.get_or_create(agent=instance)
