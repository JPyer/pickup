from django.contrib import admin

# Register your models here.


# Register your models here.

from . import models


class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission')
    list_filter = ('role_id','permission__group__name')

    # # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    # list_display_links = ('name',)


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'name', 'view_name')
    list_display_links = ('view_name',)
    list_filter = ('group_id', 'name')


admin.site.register(models.User)
admin.site.register(models.UserRole)
admin.site.register(models.PermissionGroup)
admin.site.register(models.RolePermission, RolePermissionAdmin)
admin.site.register(models.Permissions, PermissionAdmin)
