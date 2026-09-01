from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username',)

    fieldsets = UserAdmin.fieldsets + (('Role', {'fields': ('role',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Role', {'fields': ('role',)}),)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')