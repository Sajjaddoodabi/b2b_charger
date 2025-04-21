from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and is_admin(request.user)


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user and is_vendor(request.user)

    def has_object_permission(self, request, view, obj):
        return request.user and is_vendor(request.user) and obj.user == request.user


class IsVendorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and (is_admin(user) or is_vendor(user))

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user and (is_admin(user) or is_vendor(user))


def is_admin(user):
    """
    Check if the user is an admin.
    """
    return user.is_staff or user.is_superuser


def is_vendor(user):
    """
    Check if the user is a vendor.
    """
    return user.is_vendor
