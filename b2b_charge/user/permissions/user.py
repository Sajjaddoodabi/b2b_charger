from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff or request.user.is_superuser


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    

def is_admin(user):
    """
    Check if the user is an admin.
    """
    return user.is_staff or user.is_superuser
