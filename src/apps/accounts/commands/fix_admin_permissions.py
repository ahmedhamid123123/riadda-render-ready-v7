# apps/accounts/management/commands/fix_admin_permissions.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import AdminPermission

class Command(BaseCommand):
    help = "Ensure AdminPermission exists for all admin users"

    def handle(self, *args, **options):
        User = get_user_model()
        admins = User.objects.filter(role="ADMIN", is_super_admin=False)
        created = 0
        for u in admins:
            _, was_created = AdminPermission.objects.get_or_create(admin=u)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Fixed {created} admins"))
