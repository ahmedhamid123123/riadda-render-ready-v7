from django.contrib import admin
from .models import Transaction, TelecomCompany, RechargeDenomination

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'agent',
        'company',
        'denomination',
        'price',
        'status',
        'created_at',
    )

    list_filter = ('company', 'status', 'created_at')
    search_fields = ('agent__username', 'code')
    ordering = ('-created_at',)


@admin.register(TelecomCompany)
class TelecomCompanyAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_ar", "code")


@admin.register(RechargeDenomination)
class RechargeDenominationAdmin(admin.ModelAdmin):
    list_display = ("company", "value", "is_active")
    list_filter = ("company", "is_active")
    search_fields = ("company__name_ar", "company__code")
