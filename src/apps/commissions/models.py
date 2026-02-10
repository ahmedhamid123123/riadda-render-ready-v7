from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q


class Company(models.Model):
    """
    شركات الاتصالات (Asiacell, Zain, Korek...)
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class DefaultCommission(models.Model):
    """
    العمولة الافتراضية حسب الشركة والفئة
    """

    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    denomination = models.PositiveIntegerField()  # 5, 10, 15, 25
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Commission in IQD",
        default=0,
    )

    is_active = models.BooleanField(default=True)

    effective_from = models.DateTimeField(default=timezone.now)
    effective_to = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "denomination"],
                condition=Q(is_active=True),
                name="unique_active_default_commission"
            )
        ]
        indexes = [
            models.Index(fields=["company", "denomination"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.company} - {self.denomination} - {self.amount}"


class AgentCommission(models.Model):
    """
    عمولة مخصصة لوكيل
    """

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'AGENT'},
        related_name="custom_commissions"
    )

    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    denomination = models.PositiveIntegerField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Custom commission in IQD",
        default=0,
    )

    is_active = models.BooleanField(default=True)

    effective_from = models.DateTimeField(default=timezone.now)
    effective_to = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["agent", "company", "denomination"],
                condition=Q(is_active=True),
                name="unique_active_agent_commission"
            )
        ]
        indexes = [
            models.Index(fields=["agent", "company", "denomination"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.agent.username} - {self.company} - {self.denomination} - {self.amount}"


def get_effective_commission(agent, company, denomination):
    agent_commission = AgentCommission.objects.filter(
        agent=agent,
        company=company,
        denomination=denomination,
        is_active=True
    ).first()

    if agent_commission:
        return agent_commission.amount

    default_commission = DefaultCommission.objects.filter(
        company=company,
        denomination=denomination,
        is_active=True
    ).first()

    return default_commission.amount if default_commission else 0
