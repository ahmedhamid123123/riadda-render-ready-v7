from django.db import models
from django.conf import settings

class Price(models.Model):
    COMPANY_CHOICES = (
        ('ASIACELL', 'Asiacell'),
    )

    company = models.CharField(max_length=20, choices=COMPANY_CHOICES)
    denomination = models.IntegerField()  # 5 / 10 / 15 / 25
    price_to_agent = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'denomination')

    def __str__(self):
        return f"{self.company} - {self.denomination}"
class AgentBalance(models.Model):
    agent = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'AGENT'},
        related_name='agent_balance'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent.username} - Balance: {self.balance}"

class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='companies/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RechargeCategory(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    denomination = models.PositiveIntegerField()  # 5, 10, 15, 25
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.name} - {self.denomination}"
class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_audit_logs'
    )

    action = models.CharField(max_length=50, default='UNKNOWN')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    target_type = models.CharField(max_length=100, null=True, blank=True)
    target_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.created_at}"
