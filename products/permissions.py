# apps/products/permissions.py
from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Read-only for anonymous users, full access for staff.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
