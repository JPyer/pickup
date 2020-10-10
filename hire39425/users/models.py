# encoding:utf-8
import json
import pprint

from django.db import models
from datetime import datetime
from collections import defaultdict

# 引入django自带的user表，方便下方继承
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

# 继承 AbstractUser
from utils.constant import USER_ROLE_CHOICES, CLOUD_MSG_TYPE_CHOICES


class User(AbstractUser):
    # 在下方添加所扩展的字段
    table_name = "user"
    user_role = models.PositiveIntegerField(null=True, blank=True, choices=USER_ROLE_CHOICES, verbose_name="用户角色")
    role = models.ForeignKey('UserRole', related_name='users', on_delete=models.SET_NULL, null=True)
    realname = models.CharField(max_length=50, null=True, blank=True, verbose_name="用户名")
    last_login_ip = models.CharField(max_length=16, null=True, blank=True, verbose_name="上次登录ip")
    telephone = models.CharField(max_length=12, null=True, blank=True, verbose_name="手机号")
    permissions = models.ManyToManyField('Permissions', related_name='user_permission_list')
    is_active = models.BooleanField(default=True, verbose_name='启用')
    creator = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'users'

    def get_role_list(self):
        roles = [{"id": "admin", "operation": ["add", "edit", "delete"]}]
        return []

    @property
    def role_uid(self):
        return self.role.uid

    def get_role_permission_list(self):
        role_info = {
            'id': self.role.uid,
            'name': self.role.name,
            'describe': self.role.describe,
            'status': 1,
            'creatorId': self.role.uid,
            'createTime': self.date_joined,
            'deleted': 0,
            'permissions': []
        }
        permissions = self.permissions.all()
        data = {
            'roleId': 'admin',
            'permissionId': 'dashboard',
            'permissionName': '仪表盘',
            'actions': '[{"action":"add","defaultCheck":False,"describe":"新增"},{"action":"query","defaultCheck":False,"describe":"查询"},{"action":"get","defaultCheck":False,"describe":"详情"},{"action":"update","defaultCheck":False,"describe":"修改"},{"action":"delete","defaultCheck":False,"describe":"删除"}]',
            'actionEntitySet': [],
            'actionList': '',
            'dataAccess': ''
        }
        # FIXME
        permission_groups = defaultdict(dict)
        for p in permissions:
            permission_groups[p.group.uid].update({
                'roleId': self.role.uid,
                'permissionId': p.group.uid,
                'permissionName': p.group.name,
                'actionList': '',
                'dataAccess': ''
            })
            if 'actionEntitySet' not in permission_groups[p.group.uid].keys():
                permission_groups[p.group.uid]['actionEntitySet'] = []
            else:
                permission_groups[p.group.uid]['actionEntitySet'].append({
                    'action': p.view_name.split(".")[1],
                    'describe': p.name,
                    'defaultCheck': False
                })

            # print(p.group.uid, p.group.name, p.name)
        result = []
        for group, permissions in permission_groups.items():
            info = permission_groups[group]
            info['actions'] = json.dumps(info['actionEntitySet'])
            result.append(info)
        pprint.pprint(result)
        role_info['permissions'] = result
        return role_info

    def get_manage_permission_list(self):
        result = []

        permissions = self.permissions.all()
        permission_groups = defaultdict(dict)
        for p in permissions:
            permission_groups[p.group.uid].update({
                'id': self.role.uid,
                'name': self.role.name,
                'describe': self.role.describe,
                'status': 1,
                'sptDaTypes': '',
                'optionalFields': '',
                'parents': '',
                'type': '',
                'deleted': 0
            })
            if 'actions' not in permission_groups[p.group.uid].keys():
                permission_groups[p.group.uid]['actions'] = []
                permission_groups[p.group.uid]['actionData'] = []
            else:
                permission_groups[p.group.uid]['actions'].append(p.view_name.split(".")[1])
                permission_groups[p.group.uid]['actionData'].append({
                    'action': p.view_name.split(".")[1],
                    'describe': p.name,
                    'defaultCheck': False
                })

        for group, permissions in permission_groups.items():
            print("append")
            info = permission_groups[group]
            info['actionData'] = json.dumps(info['actionData'])
            result.append(info)
        return result

    def get_permission_list(self):
        role_info = {
            'id': self.username,
            'name': self.role.name,
            'describe': self.role.describe,
            'status': 1,
            'creatorId': self.role.uid,
            'createTime': self.date_joined,
            'deleted': 0,
            'permissions': []
        }
        permissions = self.permissions.all()

        permission_groups = defaultdict(dict)
        for p in permissions:
            permission_groups[p.group.uid].update({
                'roleId': self.role.uid,
                'permissionId': p.group.uid,
                'permissionName': p.group.name,
                'dataAccess': ''
            })
            if 'actionEntitySet' not in permission_groups[p.group.uid].keys():
                permission_groups[p.group.uid]['actionEntitySet'] = [
                    {'action': p.view_name,
                     'describe': p.name,
                     'defaultCheck': False
                     }
                ]
                permission_groups[p.group.uid]['actionList'] = [
                    {'action': p.view_name,
                     'describe': p.name,
                     'defaultCheck': False
                     }
                ]
                permission_groups[p.group.uid]['actionList']= [p.view_name]
            else:
                permission_groups[p.group.uid]['actionEntitySet'].append({
                    'action': p.view_name,
                    'describe': p.name,
                    'defaultCheck': False
                })
                permission_groups[p.group.uid]['actionList'].append(p.view_name)

        result = []
        for group, permissions in permission_groups.items():
            info = permission_groups[group]
            info['actions'] = json.dumps(info['actionEntitySet'])
            # info['actions'] = str(info['actionEntitySet'])
            result.append(info)
        role_info['permissions'] = result
        return role_info

    def set_role(self, role):
        self.role_id = UserRole.objects.get(uid=role).id


class UserRole(models.Model):
    table_name = "user_role"
    uid = models.CharField(max_length=32, null=False, unique=True)
    name = models.CharField(max_length=32, null=False)
    status = models.IntegerField(default=1)
    deleted = models.IntegerField(default=0)
    describe = models.TextField(null=True, verbose_name="描述")
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")
    gmt_modify = models.DateTimeField(default=datetime.now, verbose_name="更新时间")

    class Mata:
        app_label = "users"

    def __str__(self):
        return "%s %s " % (self.uid, self.name)

    def __repr__(self):
        return self.uid

class PermissionGroup(models.Model):
    table_name = "permission_group"
    name = models.CharField(max_length=32, null=False)
    uid = models.CharField(max_length=32, null=True, unique=True)
    status = models.IntegerField(default=1)
    deleted = models.IntegerField(default=0)
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")
    gmt_modify = models.DateTimeField(default=datetime.now, verbose_name="更新时间")

    class Mata:
        app_label = "users"

    def __str__(self):
        return "%s" % (self.name)


class Permissions(models.Model):
    table_name = "permissions"
    name = models.CharField(max_length=32, null=False)
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(default=1)
    deleted = models.IntegerField(default=0)
    view_name = models.CharField(max_length=64, null=True, verbose_name="视图名")
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")
    gmt_modify = models.DateTimeField(default=datetime.now, verbose_name="更新时间")

    class Mata:
        app_label = "users"

    @property
    def group_name(self):
        return self.group.name

    def __str__(self):
        return "%s %s %s" % (self.group.name, self.name, self.view_name)


class RolePermission(models.Model):
    table_name = "role_permissions"
    role = models.ForeignKey(UserRole, related_name='role_permissions', on_delete=models.CASCADE, null=True)
    permission = models.ForeignKey(Permissions, on_delete=models.CASCADE, null=True)

    class Mata:
        app_label = "users"


class UserToken(Token):
    table_name = 'user_token'

    class Mata:
        table_name = 'user_token'
        app_label = "users"


class CloudMsg(models.Model):
    table_name = 'cloud_msg'
    content = models.TextField(max_length=1000, null=False)
    msg_type = models.IntegerField(default=1, choices=CLOUD_MSG_TYPE_CHOICES, verbose_name="消息类型")
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Mata:
        app_label = "users"


class CloudSysInfo(models.Model):
    table_name = 'cloud_sys_info'
    content = models.TextField(max_length=1000, null=False)
    fw_ver = models.CharField(max_length=64, verbose_name="固件版本")
    sw_ver = models.CharField(max_length=64, verbose_name="软件版本")
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")
    publish_time = models.DateTimeField(verbose_name="发布时间")

    class Mata:
        app_label = "users"
