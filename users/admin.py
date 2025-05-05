from django.contrib import admin
from .models import UserProfile, CustomGroup, GroupPermission, UserGroup

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'employee__employee_name')

@admin.register(CustomGroup)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'description', 'created_at')
    search_fields = ('group__name', 'description')

@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'permission', 'created_at')
    list_filter = ('group', 'permission')
    search_fields = ('group__group__name', 'permission__name')

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'added_at')
    list_filter = ('group', 'added_at')
    search_fields = ('user__username', 'group__group__name')
