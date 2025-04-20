from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminAbstract
from user.models import User


@admin.register(User)
class UserAdmin(UserAdminAbstract):
    """Custom admin for User model"""

    list_display = UserAdminAbstract.list_display + ("phone_number",)
    search_fields = UserAdminAbstract.search_fields + (
        "phone_number",
        "username",
        "full_name",
    )
    fieldsets = UserAdminAbstract.fieldsets
    fieldsets[1][1]["fields"] += (
        "full_name",
        "phone_number",
        "avatar",
    )
