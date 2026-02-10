from rest_framework.permissions import BasePermission


# ======================================================
# Helpers (Django Views - user_passes_test)
# ======================================================

def is_admin(user):
    """
    Check if user is authenticated Admin
    """
    return (
        user is not None and
        user.is_authenticated and
        getattr(user, 'role', None) == 'ADMIN'
    )


def is_super_admin(user):
    """
    Check if user is Super Admin
    """
    return (
        is_admin(user) and
        getattr(user, 'is_super_admin', False) is True
    )


def is_agent(user):
    """
    Check if user is authenticated Agent
    """
    return (
        user is not None and
        user.is_authenticated and
        getattr(user, 'role', None) == 'AGENT'
    )


# ======================================================
# DRF Permissions (API)
# ======================================================

class IsAdmin(BasePermission):
    """
    API Permission:
    Allow access only to Admin users
    """
    message = 'Admin privileges required.'

    def has_permission(self, request, view):
        return is_admin(request.user)


class IsSuperAdmin(BasePermission):
    """
    API Permission:
    Allow access only to Super Admin users
    """
    message = 'Super Admin privileges required.'

    def has_permission(self, request, view):
        return is_super_admin(request.user)


class IsAgent(BasePermission):
    """
    API Permission:
    Allow access only to Agent users
    """
    message = 'Agent privileges required.'

    def has_permission(self, request, view):
        return is_agent(request.user)


# ======================================================
# Composite Permissions (جاهزة للمستقبل)
# ======================================================

class IsAdminOrSuperAdmin(BasePermission):
    """
    Allow Admin or Super Admin
    """
    message = 'Admin or Super Admin privileges required.'

    def has_permission(self, request, view):
        return is_admin(request.user)


class IsAuthenticatedAndActive(BasePermission):
    """
    Allow only authenticated & active users
    (مفيد لبعض APIs المشتركة)
    """
    message = 'Active authenticated user required.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )


def has_perm(user, perm_name):
    """
    Check admin permission safely
    """
    if not user.is_authenticated or user.role != 'ADMIN':
        return False

    # Super Admin bypass
    if getattr(user, 'is_super_admin', False):
        return True

    perms = getattr(user, 'permissions', None)
    if not perms:
        return False

    return getattr(perms, perm_name, False)
