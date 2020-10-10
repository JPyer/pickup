import json
import pprint
from datetime import datetime, timedelta
import hashlib
import time

import dateutil
from dateutil import relativedelta
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.serializers import JSONWebTokenSerializer, VerifyJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView, jwt_response_payload_handler

from device.models import DeviceList
from device.serializers import DeviceSerializer
from sg_audio_admin.settings import SECRET_KEY
from rest_framework.authentication import BaseAuthentication, TokenAuthentication

from users.authentication import JwtTokenAuth
from users.models import User, RolePermission
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions, exceptions

from users.serializers import UserSerializer, OrganizationSerializer, OrganizationUserSerializer, AuthUserSerializer, \
    LoginSerializer, ModifyPasswordSerializer
from utils.constant import *
from utils.pagination import StandardPagination
from utils.permission import UserPermission, ViewPermission
from utils.response import APIResponse


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


# 生成token
def md5(username):
    m = hashlib.md5(bytes(username, encoding='utf-8'))
    m.update(bytes(SECRET_KEY + str(time.time()), encoding='utf-8'))
    return m.hexdigest()


class LoginView(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_obj = auth.authenticate(username=request.data.get("username"), password=request.data.get("password"))
        if not user_obj:
            return APIResponse(http_status=400, message="密码验证失败")

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)

            data = {'id': user.id,
                    'name': user.username,
                    'username': user.username,
                    'password': '',
                    # 'avatar': 'https://gw.alipayobjects.com/zos/rmsportal/jZUIxmJycoymBprLOUbT.png',
                    'avatar': '',
                    'status': 1,
                    'telephone': user.telephone,
                    'lastLoginIp': user.last_login_ip,
                    'lastLoginTime': user.last_login,
                    'creatorId': user.role.uid,
                    'createTime': user.date_joined,
                    'deleted': 0,
                    'roleId': user.user_role,
                    'lang': 'zh-CN',
                    "token": token
                    }
            return APIResponse(result=data)

        errors = []
        valid_errors = []
        user = serializer.object.get('user') or request.user
        if user.is_active:
            return APIResponse(http_status=400, code=400, message="账号已禁用")

        for column, error in serializer.errors.items():
            if error:
                valid_errors.append("{}({})".format(column, str(error[0])))
        errors.append("登录失败:{}".format("|".join(valid_errors)))
        if errors:
            return APIResponse(http_status=400, code=400, message="\n".join(errors))


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"data": {}, "message": "注销成功"})


class UserRouteView(APIView):
    def get(self, request, *args, **kwargs):
        info = [
            {"router": "root", "children": [
                {"router": "dashboard", "children": ["workplace", "analysis"]},
                {"router": "form", "children": ["basicForm", "stepForm", "advanceForm"]},
                {"router": "basicForm", "name": "验权表单", "icon": "file-excel",
                 "authority": "form"}]
             }
        ]
        return Response({"code": 200, "data": info})


class UserInfoView(JSONWebTokenAPIView):
    authentication_classes = (JwtTokenAuth,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        user = valid_data['user']
        if not user:
            return APIResponse(http_status=400, status=status.HTTP_400_BAD_REQUEST)
        permissions = user.get_role_permission_list()
        info = {
            'id': user.id,
            'name': user.username,
            'username': user.username,
            'password': '',
            'avatar': '/avatar2.jpg',
            'status': 1,
            'telephone': '',
            'lastLoginIp': user.last_login_ip,
            'lastLoginTime': user.last_login,
            'creatorId': user.role.uid,
            'createTime': user.date_joined,
            'deleted': 0,
            'roleId': user.role.uid,
            'role': {}
        }
        # info['role'] = USER_MENU_ROLES
        info['role'] = permissions
        info['role']['permissions'].append(DASHBOARD_MENU_PERMISSIONS)
        return Response({"code": 200, "result": info})


class UserRoleView(APIView):
    authentication_classes = (JwtTokenAuth,)

    def get(self, request, *args, **kwargs):
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        user = valid_data['user']
        if not user:
            return APIResponse(http_status=400, status=status.HTTP_400_BAD_REQUEST)
        user_role = repr(user.role)
        if user_role == 'customer_admin':
            roles = ['org_user', 'org_admin']
            users = User.objects.filter(creator__id=user.id)
        elif user_role == 'org_admin':
            roles = ['org_user']
            users = User.objects.filter(role__uid__in=roles)
        else:
            roles = []
            users = []
        permissions = []
        for user in users:
            permissions.append(user.get_permission_list())
        # info = {"data": USER_MANAGE_ROLES}
        info = {"data": permissions}

        pprint.pprint(info['data'])

        return Response({"code": 200, "result": info, "pageSize": 50,
                         "pageNo": 0,
                         "totalPage": 1,
                         "totalCount": len(permissions)})


class UserPermissionView(APIView):
    authentication_classes = (JwtTokenAuth,)

    def get(self, request, *args, **kwargs):
        token = {"token": ""}

        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        user = valid_data['user']
        # info = {"data": USER_MANAGE_PERMISSIONS}
        info = {"data": user.get_manage_permission_list()}

        return Response({"code": 200, "result": info, "pageSize": 50,
                         "pageNo": 0,
                         "totalPage": 1,
                         "totalCount": 57})


class ModifyPasswordView(APIView):
    permission_classes = [UserPermission]

    def post(self, request):
        token = {"token": ""}
        serializer = ModifyPasswordSerializer(data=request.data)
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        user = valid_data['user']
        old_password = request.data.get("old_password")
        password = request.data.get("password")
        re_password = request.data.get("re_password")
        errors = []
        user_obj = auth.authenticate(username=user.username, password=old_password)
        if not user_obj:
            return APIResponse(code=400, message="旧密码验证失败")
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            valid_errors = []
            for column, error in serializer.errors.items():
                if error:
                    valid_errors.append("{}({})".format(column, str(error[0])))
            print(serializer.errors)
            errors.append("修改失败:{}".format("|".join(valid_errors)))
            if errors:
                return APIResponse(code=400, message="\n".join(errors))
        if password and password == re_password:
            user.password = make_password(password)
            user.save()
            return APIResponse(code=200, message="密码修改成功")
        return APIResponse(code=400, message="请确认输入的密码是否正确")


class CustomerView(object):
    """客户管理"""
    permission_classes = [UserPermission, ViewPermission]

    def post(self):
        info = {}
        return Response({"code": 200, "result": info})

    def get(self):
        info = {}
        return Response({"code": 200, "result": info})

    def delete(self):
        return Response({"code": 200, "result": {}})


class CustomerListView(object):
    permission_classes = [UserPermission, ViewPermission]

    def get(self):
        info = {}
        return Response({"code": 200, "result": info})


class OrganizationListView(GenericViewSet, ListModelMixin):
    """机构管理"""
    authentication_classes = (JwtTokenAuth,)
    queryset = User.objects.filter(role__uid='org_admin')
    serializer_class = OrganizationSerializer
    pagination_class = StandardPagination
    permission_classes = [UserPermission, ViewPermission]

    def list(self, request, *args, **kwargs):

        queryset = self._filter(request=request)
        if queryset is None:
            return APIResponse(status='fail', message='params is empty')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _filter(self, request):
        params = request.query_params
        device_id = params.get('id', None)
        status = params.get('status', None)
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        user = valid_data['user']
        if user and user.role.uid == 'customer_admin':
            queryset = User.objects.filter(role__uid__in=('org_user', 'org_admin'))
        else:
            queryset = self.filter_queryset(self.get_queryset())

        if device_id:
            queryset = self.get_queryset().filter(id=device_id)
        if status:
            queryset = self.get_queryset().filter(status=status)

        queryset = queryset.filter(creator_id=user.id)
        queryset = self.filter_queryset(queryset).order_by('-id')

        return queryset


class OrganizationView(GenericAPIView):
    """机构视图"""
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]

    def post(self, request):
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        current_user = valid_data['user']
        # 添加
        serializer = AuthUserSerializer(data=request.data)
        errors = []
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            valid_errors = []
            for column, error in serializer.errors.items():
                if error:
                    valid_errors.append("{}({})".format(column, str(error[0])))

            errors.append("创建失败:{}".format("|".join(valid_errors)))
            if errors:
                return APIResponse(code=400, message="\n".join(errors))

        password = serializer.validated_data['password']
        serializer.validated_data['password'] = make_password(password)
        user_data = serializer.data
        user_data['role_id'] = serializer.get_role('org_admin')

        user_data['creator_id'] = current_user.id
        user_obj = User.objects.create(**user_data)

        # 获取role org_admin 默认权限
        role_permissions = RolePermission.objects.filter(role__uid='org_admin')
        for role_per in role_permissions:
            user_obj.permissions.add(role_per.permission)
        user_obj.save()
        return APIResponse(message='添加成功')

    def put(self, request):
        # 更新
        data = request.data
        # 校验是否当前用户
        serializer = OrganizationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user_obj = User.objects.get(id=data.get('id'))
            except Exception as e:
                return APIResponse(code=400, message='用户不存在')
            user_id = data.get('id')
            del data['id']
            data['is_active'] = 1 if request.data['is_active'] else 0
            # data['is_active'] = True
            user_obj.realname = 'test_new_org'
            user_obj.is_active = request.data['is_active']
            user_obj.is_delete = False
            user_obj.save(using='default')
            # User.objects.using('default').update(id=user_id, **data)
        return APIResponse(code=200, message='更新成功')

    def delete(self, request):
        # 删除
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        current_user = valid_data['user']
        user_id = request.data
        user_obj = User.objects.get(id=user_id)

        if user_obj:
            if user_obj.creator.id == current_user.id:
                user_obj.delete()
                return APIResponse(message="删除成功")
            elif user_obj.creator and user_obj.creator.creator == current_user.id:
                user_obj.delete()
                return APIResponse(message="删除成功")
            else:
                return APIResponse(code=500, message="非管理员或该用户创建者无权操作")

class OrganizationUserView(APIView):
    """机构用户"""
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]

    def post(self, request):
        # 添加
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        current_user = valid_data['user']
        # 添加
        serializer = AuthUserSerializer(data=request.data)
        errors = []
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            valid_errors = []
            for column, error in serializer.errors.items():
                if error:
                    valid_errors.append("{}({})".format(column, str(error[0])))

            errors.append("创建失败:{}".format("|".join(valid_errors)))
            if errors:
                return APIResponse(code=400, message="\n".join(errors))

        password = serializer.validated_data['password']
        serializer.validated_data['password'] = make_password(password)
        user_data = serializer.data
        user_data['role_id'] = serializer.get_role('org_user')

        user_data['creator_id'] = current_user.id
        user_obj = User.objects.create(**user_data)

        # 获取role org_user 默认权限
        role_permissions = RolePermission.objects.filter(role__uid='org_role')
        for role_per in role_permissions:
            user_obj.permissions.add(role_per.permission)
        user_obj.save()
        return APIResponse(message='添加成功')

    def delete(self, request):
        # 删除
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        current_user = valid_data['user']
        user_id = request.data
        user_obj = User.objects.get(id=user_id)

        if user_obj:
            if user_obj.creator.id == current_user.id:
                user_obj.delete()
                return APIResponse(message="删除成功")
            elif user_obj.creator and user_obj.creator.creator == current_user.id:
                user_obj.delete()
                return APIResponse(message="删除成功")
            else:
                return APIResponse(code=500, message="非管理员或该用户创建者无权操作")
        return APIResponse(code=500, message="删除失败")


class OrganizationUserListView(GenericViewSet, ListModelMixin):
    """机构用户列表视图"""
    authentication_classes = (JwtTokenAuth,)
    queryset = User.objects.filter(role__uid='org_user')
    serializer_class = OrganizationUserSerializer
    pagination_class = StandardPagination
    permission_classes = [UserPermission, ViewPermission]

    def list(self, request, *args, **kwargs):

        queryset = self._filter(request=request)
        if queryset is None:
            return APIResponse(status='fail', message='params is empty')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _filter(self, request):
        params = request.query_params
        user_id = params.get('id', None)
        status = params.get('status', None)
        role = params.get('role', None)
        token = {"token": ""}
        token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
        valid_data = VerifyJSONWebTokenSerializer().validate(token)
        user = valid_data['user']
        queryset = self.get_queryset()

        if user_id:
            queryset = queryset.filter(id=user_id)
        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.filter(creator_id=user.id)
        queryset = self.filter_queryset(queryset).order_by('-id')

        return queryset
