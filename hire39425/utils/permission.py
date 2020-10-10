# encoding:utf-8
import pprint
import re

from rest_framework.permissions import BasePermission
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


class MyPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        """控制对obj对象的访问权限，此案例决绝所有对对象的访问"""
        return False


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        # 认证类中返回了token_obj.user, request_token

        # request.user为当前用户对象
        if request.user:
            print("requ", request.user)
            try:
                token = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
                valid_data = VerifyJSONWebTokenSerializer().validate({'token': token})
                user = valid_data['user']
            except Exception as e:
                return False
            if user:
                return True
            return False
        else:
            return False


class ViewPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate({'token': token})
        user = valid_data['user']
        user_permssions = user.permissions.all()
        # pprint.pprint(view.__dict__)
        try:
            getattr(view, 'head')
        except AttributeError as e:
            allow_methods = view.headers['Allow']
            return allow_methods.find(request.method) >= 0
        else:

            func_name = re.findall(r"function (.*?) at", str(view.head.__func__))[0]
            user_view_permissions = filter(lambda p: p.view_name == func_name, user_permssions)
            if len(list(user_view_permissions)) > 0:
                return True

        return False

    def has_perms(self, user, perms):
        pass

    def has_object_permission(self, request, view, obj):
        """控制对obj对象的访问权限，此案例决绝所有对对象的访问"""
        print('view has_object_permission {} {}'.format(view, obj))
        return True

    def get_module_perms(self, view):
        return ['api.{}'.format(per) for per in view.module_perms]


class GetFileViewPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            token = request.query_params.get("token")
            valid_data = VerifyJSONWebTokenSerializer().validate({'token': token})
            user = valid_data['user']
        except Exception as e:
            return False

        user_permssions = user.permissions.all()

        try:
            getattr(view, 'head')
        except AttributeError as e:
            allow_methods = view.headers['Allow']
            return allow_methods.find(request.method) >= 0
        else:

            func_name = re.findall(r"function (.*?) at", str(view.head.__func__))[0]
            user_view_permissions = filter(lambda p: p.view_name == func_name, user_permssions)
            if len(list(user_view_permissions)) > 0:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """控制对obj对象的访问权限，此案例决绝所有对对象的访问"""
        print('view has_object_permission {} {}'.format(view, obj))
        return True
