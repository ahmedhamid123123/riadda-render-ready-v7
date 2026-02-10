"""Commission lookup service.

This project has a newer Sales domain model (TelecomCompany / RechargeDenomination)
while the commissions app historically used its own Company model + int denomination.

To keep the project working without a risky migration, we bridge the two:
- If `company` is a TelecomCompany, we match/create commissions.Company by `code`.
- If `denomination` is a RechargeDenomination, we use `denomination.value`.
"""

from apps.commissions.models import DefaultCommission, AgentCommission, Company

def get_commission_amount(agent, company, denomination):
    """
    Returns commission amount (IQD) for an agent and denomination.
    Priority:
    1. AgentCommission (override)
    2. DefaultCommission
    """

    # 1️⃣ عمولة مخصصة للوكيل
    # --- Bridge new Sales models -> commissions schema ---
    # company: TelecomCompany or commissions.Company
    if not isinstance(company, Company):
        company_code = getattr(company, "code", None)
        company_name = getattr(company, "name_ar", None) or getattr(company, "name", None) or (company_code or "")
        if company_code:
            company, _ = Company.objects.get_or_create(
                code=company_code,
                defaults={"name": str(company_name)[:100] or company_code},
            )

    # denomination: RechargeDenomination or int
    denom_value = getattr(denomination, "value", None)
    if denom_value is None:
        denom_value = denomination

    # 1️⃣ عمولة مخصصة للوكيل
    agent_commission = AgentCommission.objects.filter(
        agent=agent,
        company=company,
        denomination=denom_value,
        is_active=True,
    ).first()

    if agent_commission:
        return agent_commission.amount

    # 2️⃣ عمولة افتراضية
    default_commission = DefaultCommission.objects.filter(
        company=company,
        denomination=denom_value,
        is_active=True,
    ).first()

    if default_commission:
        return default_commission.amount

    # 3️⃣ إذا ماكو شي
    return 0
