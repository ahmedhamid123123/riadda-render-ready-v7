from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import AuditLog
from django.contrib import admin
from .models import SystemSetting

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )



@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'actor',
        'action',
        'target_user',
        'transaction_id',
        'created_at'
    )
    list_filter = ('action', 'created_at')
    search_fields = ('actor__username', 'message')
    readonly_fields = (
        'actor',
        'action',
        'target_user',
        'transaction_id',
        'message',
        'created_at'
    )



@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key',)
