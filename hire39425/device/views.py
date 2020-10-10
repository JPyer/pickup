# encoding:utf-8

from django.shortcuts import render

from django.http import HttpResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

import cache
from device.serializers import DeviceSerializer, DeviceGroupSerializer, DeviceAudioChannelSerializer, \
    DeviceAudioSetSerializer
from users.authentication import JwtTokenAuth
from utils.constant import DeviceStatusEnum
from utils.pagination import StandardPagination
from utils.permission import UserPermission, ViewPermission
from utils.response import APIResponse
from rest_framework import viewsets, permissions

from device.models import DeviceList, DeviceGroup
from utils.sg_device_helper import SgDeviceHelper


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = DeviceList.objects.all()
    serializer_class = DeviceSerializer

    authentication_classes = (SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated]


class DeviceDiscoveryView(APIView):
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]

    def get(self, request):
        device_list = SgDeviceHelper.search_device()
        if not device_list:
            device_list = []
            message = '没查找到设备,请确认设备是否打开并处于同一局域网网段中'
        else:
            message = '查找到{}台设备'.format(len(device_list))
        return APIResponse(
            data=device_list,
            code=200,
            message=message)


class DeviceView(APIView):
    authentication_classes = (JwtTokenAuth,)

    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        # 获取
        params = request.query_params
        device_id = params.get("device_id")
        if not device_id:
            return APIResponse(message='参数不合法', code=404, http_status=404)
        obj = DeviceList.objects.get(device_id=device_id)
        serializer = DeviceSerializer(obj)
        return APIResponse(result=serializer.data)

    def post(self, request):
        # 添加
        dataset = request.data.get("dataset")
        if dataset:
            errors = []
            for index, info in enumerate(dataset):
                serializer = DeviceSerializer(data=info)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print(serializer.errors)
                    valid_errors = []
                    for error in serializer.errors.values():
                        if error:
                            valid_errors.append(str(error[0]))
                    errors.append("第{}条记录验证失败:{}".format(index + 1, "|".join(valid_errors)))
            if errors:
                return APIResponse(code=400, message="\n".join(errors))
            return APIResponse(message='添加成功')
        else:
            serializer = DeviceSerializer(data=request.data)
            ip_addr = request.data.get("ip_addr")
            # online_device_list = cache.ONLINE_DEVICE_LIST
            online_device_list = cache.CurDevices.get_device_list()
            if online_device_list and ip_addr in [d['ip_addr'] for d in online_device_list]:
                if serializer.is_valid():
                    post = serializer.save()
                    return APIResponse(message='添加成功')

            check_device = DeviceList.objects.filter(ip_addr=ip_addr)
            if check_device:
                return APIResponse(code=400, message='添加失败,该设备ip已存在系统中，请确认后重试')
            return APIResponse(code=400, message='添加失败,没找到对应ip')

    def delete(self, request):
        # 删除
        device_id = request.data
        print(device_id)
        device_obj = DeviceList.objects.get(id=device_id)
        if device_obj:
            device_obj.delete(
            )
            return APIResponse(message="删除成功")
        return APIResponse(code=500, message="删除失败，没找到该设备id")

    def put(self, request):
        # 更新
        data = request.data
        # 校验是否当前用户
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            check_device = DeviceList.objects.filter(ip_addr=data.get('ip_addr'))
            if check_device:
                return APIResponse(code=400, message='添加失败,该ip地址已存在系统中，请确认后重试')
            device_id = data.get('id')
            del data['id']
            DeviceList.objects.update_or_create(id=device_id, defaults=data)
        return APIResponse(code=200, message='更新成功')


class DeviceAudioChannelView(APIView):
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]

    def get(self, request):
        params = request.query_params
        device_id = params.get("device_id")
        obj = DeviceList.objects.get(id=device_id)

        serializer = DeviceAudioChannelSerializer(obj)
        return APIResponse(result=serializer.data)

    def put(self, request):
        # 修改
        data = request.data
        serializer = DeviceAudioChannelSerializer(data=request.data)
        if serializer.is_valid():
            print(data)
            device_id = data.get('id')
            if not device_id:
                return APIResponse(http_status=400, message='非法请求')
            del data['id']
            DeviceList.objects.update_or_create(id=device_id, defaults=data)

        return APIResponse(message='修改成功')


class DeviceAudioSetView(APIView):
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]

    def get(self, request):
        params = request.query_params
        device_id = params.get("device_id")
        obj = DeviceList.objects.get(id=device_id)

        serializer = DeviceAudioSetSerializer(obj)
        return APIResponse(result=serializer.data)

    def put(self, request):
        # 修改
        data = request.data
        serializer = DeviceAudioChannelSerializer(data=request.data)
        if serializer.is_valid():
            device_id = data.get('device_id')
            if not device_id:
                return APIResponse(http_status=400, message='非法请求')
            del data['id']
            DeviceList.objects.update_or_create(id=device_id, defaults=data)

        return APIResponse(message='修改成功')


class DeviceGroupView(APIView):
    authentication_classes = (JwtTokenAuth,)

    permission_classes = [UserPermission, ViewPermission]

    def get(self, request):
        # 获取
        params = request.query_params
        group_id = params.get("group_id")
        if not group_id:
            return APIResponse(message='参数不合法', code=404, http_status=404)
        obj = DeviceGroup.objects.get(id=group_id)

        serializer = DeviceGroupSerializer(obj)
        return APIResponse(result=serializer.data)

    def post(self, request):
        # 添加
        serializer = DeviceGroupSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()

        return APIResponse(message='添加成功')

    def delete(self, request):
        # 删除
        group_id = request.data
        print(group_id)
        device_group_obj = DeviceGroup.objects.get(id=group_id)
        if device_group_obj:
            device_group_obj.delete(
            )
            return APIResponse(message="删除成功")
        return APIResponse(code=500, message="删除失败，没找到该设备id")

    def put(self, request):
        # 更新
        data = request.data
        serializer = DeviceGroupSerializer(data=request.data)
        if serializer.is_valid():
            group_id = data.get('id')
            defaults = {"name": data.get("name")}
            DeviceGroup.objects.update_or_create(id=group_id, defaults=defaults)
        return APIResponse(code=200, message='更新成功')


class DeviceGroupListView(GenericViewSet, ListModelMixin):
    """设备分组管理"""
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer
    pagination_class = StandardPagination

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

    def options(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        return APIResponse(data=serializer.data)

    def _filter(self, request):
        params = request.query_params
        name = params.get('name', None)

        queryset = self.filter_queryset(self.get_queryset())
        if name:
            queryset = self.get_queryset().filter(name__contains=name)

        queryset = self.filter_queryset(queryset).order_by('-id')

        return queryset


class DeviceListView(GenericViewSet, ListModelMixin):
    """设备管理"""
    authentication_classes = (JwtTokenAuth,)
    queryset = DeviceList.objects.all()
    serializer_class = DeviceSerializer
    pagination_class = StandardPagination
    permission_classes = [UserPermission, ViewPermission]

    def list(self, request, *args, **kwargs):

        queryset = self._filter(request=request)
        if queryset is None:
            return APIResponse(status='fail', message='params is empty')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            device_list = serializer.data
            online_device_list = cache.CurDevices.get_device_list()
            print("cached device:", online_device_list)
            online_product_ids = []
            if online_device_list:
                online_product_ids = [d['product_id'] for d in online_device_list]

            new_device_list = []
            for d in device_list:
                if d['product_id'] in online_product_ids:
                    if d['status'] != DeviceStatusEnum.RECORDING.value:
                        d['status'] = DeviceStatusEnum.RUNNING.value
                else:
                    d['status'] = DeviceStatusEnum.DEFAULT.value
                DeviceList.objects.filter(product_id=d['product_id']).update(status=d['status'])
                new_device_list.append(d)
            return self.get_paginated_response(new_device_list)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _filter(self, request):
        params = request.query_params
        device_id = params.get('id', None)
        status = params.get('status', None)
        group_id = params.get('group_id', None)

        queryset = self.filter_queryset(self.get_queryset())
        if device_id:
            queryset = self.get_queryset().filter(id=device_id)
        if status:
            queryset = self.get_queryset().filter(status=status)
        if group_id:
            queryset = self.get_queryset().filter(device_group_id=group_id)
        queryset = self.filter_queryset(queryset).order_by('-id')

        return queryset

    def options(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        return APIResponse(data=serializer.data)
