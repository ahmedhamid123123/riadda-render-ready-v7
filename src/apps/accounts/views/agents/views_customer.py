from django.shortcuts import render
from apps.billing.models import Company

def customer_recharge_view(request):
    companies = Company.objects.filter(
        is_active=True
    ).prefetch_related(
        'categories'
    )

    return render(request, 'customer/recharge_list.html', {
        'companies': companies
    })
