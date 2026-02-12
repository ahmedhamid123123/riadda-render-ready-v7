"""
Smoke test script for API endpoints.
Creates an agent user, obtains JWT via AgentLoginAPIView, and calls
`api/app/commissions/effective/` and `api/app/billing/agent/balance/`.

Run:
    python scripts/smoke_test_api.py
"""
import os
import django
import json
import sys
from pathlib import Path

# Ensure src/ is on PYTHONPATH (same as manage.py)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.commissions.models import Company, DefaultCommission
from decimal import Decimal

User = get_user_model()

client = APIClient()

# Create test agent
username = "smoke_agent"
password = "testpass123"

agent, created = User.objects.get_or_create(username=username, defaults={
    "role": "AGENT",
    "full_name": "Smoke Agent",
    "is_active": True,
})
if created:
    agent.set_password(password)
    agent.save()
else:
    agent.set_password(password)
    agent.save()

# Ensure a company + default commission exists
company_code = "ASIACELL"
company, _ = Company.objects.get_or_create(code=company_code, defaults={"name": "Asiacell"})
DefaultCommission.objects.get_or_create(company=company, denomination=10, defaults={"amount": Decimal("100")})

# Obtain JWT via agent app login endpoint
resp = client.post('/api/app/accounts/agent/login/', {
    'username': username,
    'password': password
}, format='json')
print('LOGIN status:', resp.status_code)
print(resp.data)

if resp.status_code == 200:
    token = resp.data.get('data', {}).get('access_token') or resp.data.get('data', {}).get('access_token')
    # The AgentLoginAPIView returns keys 'access_token' and 'refresh_token' under data
    if not token:
        # The accounts app auth_views AgentLoginAPIView returns 'access_token' key
        token = resp.data.get('data', {}).get('access_token') if isinstance(resp.data.get('data'), dict) else None
    if not token:
        # Some endpoints return top-level 'access'/'refresh' for AdminLogin; try alternative keys
        token = resp.data.get('data', {}).get('access_token') if isinstance(resp.data.get('data'), dict) else None

    if not token:
        print('Could not find access token in login response; full response:')
        print(json.dumps(resp.data, default=str, indent=2))
    else:
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Call commissions effective endpoint
        r2 = client.get(f'/api/app/commissions/effective/?company_code={company_code}&denomination=10')
        print('COMMISSIONS effective status:', r2.status_code)
        print(r2.data)

        # Call billing agent balance endpoint
        r3 = client.get('/api/app/billing/agent/balance/')
        print('BILLING balance status:', r3.status_code)
        print(r3.data)
else:
    print('Login failed; cannot proceed to protected endpoints.')
