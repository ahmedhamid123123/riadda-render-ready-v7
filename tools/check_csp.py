import importlib.util
import importlib.metadata

spec = importlib.util.find_spec('csp')
print('csp spec:', spec)
try:
    v = importlib.metadata.version('django-csp')
    print('django-csp version:', v)
except importlib.metadata.PackageNotFoundError:
    print('django-csp not installed')
