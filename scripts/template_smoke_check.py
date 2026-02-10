import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import sys
import pathlib

# Ensure project `src` is on sys.path so `config` package is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src'))

import django
from django.template import loader, TemplateSyntaxError
from django.test import RequestFactory


def make_dummy_request():
    factory = RequestFactory()
    req = factory.get('/')

    class DummyUser:
        is_authenticated = False
        role = None
        is_super_admin = False
        username = 'anonymous'
        permissions = None

    req.user = DummyUser()
    req.session = {}
    return req


def render_templates(names):
    django.setup()
    req = make_dummy_request()
    failures = []

    base_context = {
        'request': req,
        'messages': [],
        'SHOW_PROFIT': False,
        'ALLOW_AGENT_USERNAME_EDIT': False,
        'perms': type('P', (), {
            'is_super_admin': False,
            'can_add_agents': False,
            'can_view_agents': False,
            'can_edit_agents': False
        })(),
    }

    for name in names:
        try:
            tpl = loader.get_template(name)

            # Provide per-template extra context for templates that expect objects
            extra = {}
            if name == 'accounts/agent_detail.html':
                class Agent:
                    id = 1
                    username = 'agent1'
                    is_active = True

                extra = {
                    'agent': Agent(),
                    'balance': 1000,
                    'current_amount': 1000,
                    'last_amount': 800,
                    'current_count': 5,
                    'last_count': 3,
                    'change_percentage': 25.0,
                    'status_filter': '',
                    'date_from': '',
                    'date_to': '',
                    'page_obj': type('P', (), {'__iter__': lambda s: iter([]), 'paginator': type('Q', (), {'num_pages': 1}), 'has_other_pages': False, 'has_previous': False, 'has_next': False, 'number': 1})(),
                }

            context = dict(base_context)
            context.update(extra)
            tpl.render(context)
            print(f'OK: {name}')
        except TemplateSyntaxError as e:
            print(f'TemplateSyntaxError in {name}: {e}')
            failures.append((name, str(e)))
        except Exception:
            tb = traceback.format_exc()
            print(f'ERROR rendering {name}:')
            print(tb)
            failures.append((name, tb))

    return failures


if __name__ == '__main__':
    templates = [
        'base/base.html',
        'base/navbar.html',
        'accounts/login.html',
        'accounts/dashboard.html',
        'accounts/agents.html',
        'accounts/agent_detail.html',
        'accounts/agent_transactions.html',
        'accounts/agent_dashboard.html',
        'admin/catalog/company_form.html',
        'receipt/receipt.html',
    ]

    failures = render_templates(templates)
    if failures:
        print('\nTemplate smoke-check completed: FAILURES detected')
        for name, err in failures:
            print('---', name)
            print(err)
        sys.exit(2)
    else:
        print('\nTemplate smoke-check completed: all OK')
        sys.exit(0)
