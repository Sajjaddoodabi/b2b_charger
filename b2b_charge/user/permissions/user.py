from rest_framework.permissions import BasePermission
from vendor.models import Vendor


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff or request.user.is_superuser


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_vendor

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_vendor and obj.user == request.user


def is_admin(user):
    """
    Check if the user is an admin.
    """
    return user.is_staff or user.is_superuser
