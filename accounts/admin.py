from django.contrib import admin

from accounts.models import User, Role , Permission

admin.site.register(User)
admin.site.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'permission_count')
    search_fields = ('name',)
    list_filter = ('permissions',)

admin.site.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active','permission_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

    def permission_count(self, obj):
        return obj.permissions.count()

    permission_count.short_description = 'Permissions'


# Register your models here.
