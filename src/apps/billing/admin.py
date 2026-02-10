from django.contrib import admin
from .models import Price, AgentBalance

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('company', 'denomination', 'price_to_agent', 'is_active')
    list_filter = ('company', 'is_active')
    ordering = ('company', 'denomination')

@admin.register(AgentBalance)
class AgentBalanceAdmin(admin.ModelAdmin):
    list_display = ('agent', 'balance', 'updated_at')
    search_fields = ('agent__username',)
