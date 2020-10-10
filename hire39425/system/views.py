# encoding:utf-8
import datetime

from django.shortcuts import render

from django.http import HttpResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

import cache
from audio.models import AudioList
from device.serializers import DeviceSerializer, DeviceGroupSerializer, DeviceAudioChannelSerializer, \
    DeviceAudioSetSerializer
from system.models import SystemInfo, SystemMessage
from system.serializers import SysMsgSerializer
from users.authentication import JwtTokenAuth
from utils.pagination import StandardPagination
from utils.permission import UserPermission, ViewPermission
from utils.response import APIResponse
from rest_framework import viewsets, permissions

from device.models import DeviceList, DeviceGroup
from utils.sg_device_helper import SgDeviceHelper


class SystemInfoView(APIView):
    authentication_classes = (JwtTokenAuth,)

    permission_classes = [UserPermission]

    def get(self, request):
        # 获取
        system_info = SystemInfo.objects.first()
        params = request.query_params
        current_run_time = (datetime.datetime.now() - cache.START_RUNNING_TIME).seconds
        if current_run_time < 60:
            time_unit = "秒"
        elif current_run_time < 3600:
            current_run_time = round((current_run_time / 60), 0)
            time_unit = "分钟"
        else:
            current_run_time = round((current_run_time / 3600), 0)
            time_unit = "小时"
        audio_count = AudioList.objects.count()
        result = {
            "status": "运行中",
            "run_time": current_run_time,
            "audio_count": audio_count,
            "time_unit": time_unit,
            "audio_storage_size": 200,
            "firmware_version": system_info.firmware_version,
            "software_version": system_info.software_version
        }
        return APIResponse(result=result)


class SystemMsgView(GenericViewSet, ListModelMixin):
    authentication_classes = (JwtTokenAuth,)
    serializer_class = SysMsgSerializer
    permission_classes = [UserPermission]
    queryset = SystemMessage.objects.all()
    pagination_class = StandardPagination

    def list(self, request, *args, **kwargs):
        queryset = self._filter(request=request)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _filter(self, request):
        params = request.query_params
        unread = int(params.get('unread', 0))
        queryset = self.filter_queryset(self.get_queryset())
        if unread:
            queryset = queryset.filter(unread=unread)
        else:
            SystemMessage.objects.filter(unread=True).update(unread=False)
        queryset = queryset.order_by('-id')
        return queryset
