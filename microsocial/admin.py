# coding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from microsocial.models import User


class CustomUserAdmin(UserAdmin):
    form = UserChangeFrom
    add_form = UserCreationFrom
    list_display = ('email', 'name', 'is_staff')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')
        }),
    )
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'classes': ('wide',),
            'fields': ('name',)
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'classes': ('wide',),
            'fields': ('last_login', 'date_joined')
        }),
    )
    search_fields = ('email', 'name',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
