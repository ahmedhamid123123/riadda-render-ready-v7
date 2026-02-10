from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from apps.accounts.permissions import is_admin
from apps.sales.models import TelecomCompany, RechargeDenomination
from django.conf import settings
from apps.core.utils.uploads import validate_uploaded_image


# =========================
# Companies
# =========================
@login_required
@user_passes_test(is_admin)
def admin_companies_list(request):
    companies = TelecomCompany.objects.all().order_by("display_order", "name_ar")
    return render(request, "admin/catalog/companies_list.html", {
        "companies": companies
    })


@login_required
@user_passes_test(is_admin)
def admin_company_create(request):
    if request.method == "POST":
        logo_file = request.FILES.get("logo")
        valid, err = validate_uploaded_image(logo_file)
        if not valid:
            messages.error(request, err or "Invalid upload")
            return redirect("admin-companies")

        TelecomCompany.objects.create(
            code=request.POST.get("code"),
            name_ar=request.POST.get("name_ar"),
            company_type=request.POST.get("company_type"),
            display_order=int(request.POST.get("display_order", 0)),
            is_active=("is_active" in request.POST),
            logo=logo_file,
        )
        messages.success(request, "تمت إضافة الشركة بنجاح")
        return redirect("admin-companies")

    return render(request, "admin/catalog/company_form.html")


@login_required
@user_passes_test(is_admin)
def admin_company_edit(request, company_id):
    company = get_object_or_404(TelecomCompany, id=company_id)

    if request.method == "POST":
        company.code = request.POST.get("code")
        company.name_ar = request.POST.get("name_ar")
        company.company_type = request.POST.get("company_type")
        company.display_order = int(request.POST.get("display_order", 0))
        company.is_active = ("is_active" in request.POST)

        logo_file = request.FILES.get("logo")
        if logo_file:
            valid, err = validate_uploaded_image(logo_file)
            if not valid:
                messages.error(request, err or "Invalid upload")
                return redirect("admin-companies")
            company.logo = logo_file

        company.save()
        messages.success(request, "تم تحديث الشركة")
        return redirect("admin-companies")

    return render(request, "admin/catalog/company_form.html", {
        "company": company
    })


# =========================
# Denominations
# =========================
@login_required
@user_passes_test(is_admin)
def admin_denominations_list(request):
    denoms = (
        RechargeDenomination.objects
        .select_related("company")
        .order_by("company__name_ar", "value")
    )
    return render(request, "admin/catalog/denominations_list.html", {
        "denominations": denoms
    })


@login_required
@user_passes_test(is_admin)
def admin_denomination_create(request):
    companies = TelecomCompany.objects.filter(is_active=True)

    if request.method == "POST":
        RechargeDenomination.objects.create(
            company_id=request.POST.get("company_id"),
            product_type=request.POST.get("product_type"),
            value=int(request.POST.get("value")),
            price_to_agent=request.POST.get("price_to_agent"),
            cost_to_company=request.POST.get("cost_to_company", 0),
            is_active=("is_active" in request.POST),
        )
        messages.success(request, "تمت إضافة الفئة بنجاح")
        return redirect("admin-denominations")

    return render(request, "admin/catalog/denomination_form.html", {
        "companies": companies
    })


@login_required
@user_passes_test(is_admin)
def admin_denomination_edit(request, denom_id):
    denom = get_object_or_404(RechargeDenomination, id=denom_id)
    companies = TelecomCompany.objects.filter(is_active=True)

    if request.method == "POST":
        denom.company_id = request.POST.get("company_id")
        denom.product_type = request.POST.get("product_type")
        denom.value = int(request.POST.get("value"))
        denom.price_to_agent = request.POST.get("price_to_agent")
        denom.cost_to_company = request.POST.get("cost_to_company", 0)
        denom.is_active = ("is_active" in request.POST)
        denom.save()

        messages.success(request, "تم تحديث الفئة")
        return redirect("admin-denominations")

    return render(request, "admin/catalog/denomination_form.html", {
        "denomination": denom,
        "companies": companies
    })
