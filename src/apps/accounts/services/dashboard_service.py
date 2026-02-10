from django.db.models import Sum, Count
from django.utils.timezone import now
from apps.sales.models import Transaction


def get_admin_dashboard_metrics():
    today = now().date()
    qs = Transaction.objects.filter(created_at__date=today, status="CONFIRMED")

    return {
        "total_sales": qs.aggregate(s=Sum("amount"))["s"] or 0,
        "total_transactions": qs.count(),
        "recent_transactions": Transaction.objects.order_by("-created_at")[:10],
    }
