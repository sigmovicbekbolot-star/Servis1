# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # Формада көрүнө турган талаалар
    fieldsets = (
        (None, {'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'managed_building')}),
    )

    # Көрүнө турган талаалар тизмеси (лист view)
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
