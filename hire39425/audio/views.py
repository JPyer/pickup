# encoding:utf-8
import asyncio
import datetime
import mimetypes
import os
import re
import stat
import time
from wsgiref.util import FileWrapper

from django.http import HttpResponse, FileResponse, HttpResponseNotModified
from django.utils.http import http_date
from django.views.static import was_modified_since
from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

import cache
from audio.serializers import AudioSerializer
from device.models import DeviceList
from users.authentication import JwtTokenAuth
from audio.models import AudioList
from utils.constant import DeviceStatusEnum
from utils.pagination import StandardPagination
from utils.permission import ViewPermission, UserPermission, GetFileViewPermission
from utils.response import APIResponse
from django.http import StreamingHttpResponse

from utils.sg_device_helper import SgDeviceHelper


def read_file(file_name, chunk_size=512):
    with open(file_name, "rb") as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


class AudioFileView(APIView):
    # TODO
    # authentication_classes = (JwtTokenAuth,)
    permission_classes = [GetFileViewPermission]

    def get(self, request):
        params = request.query_params

        audio_id = params.get("id")
        token = params.get("token")
        if not audio_id:
            return APIResponse(message='参数不合法', code=404, http_status=400)
        obj = AudioList.objects.get(id=audio_id)

        dir_path = os.path.join(os.path.abspath("."), 'media')
        # TODO
        # file_path = dir_path + "/" + "[NONAME]-D20201002T043801-16k-1ch-24bit.pcm"
        # file_path = dir_path + "/" + "[NONAME]-D20201002T180209-16k-1ch-24bit_16000Hz_24bitWAV.wav"
        # if obj.file_path.endswith("pcm"):
        #     return APIResponse(message='系统暂不支持pcm格式音频回播', code=400, http_status=400)

        file_path = dir_path + "/" + obj.file_path

        #
        # # 计算读取文件的起始位置
        # start_bytes = re.search(r'bytes=(\d+)-', request.META.get('HTTP_RANGE', ''), re.S)
        # start_bytes = int(start_bytes.group(1)) if start_bytes else 0
        #
        # # 打开文件并移动下标到起始位置，客户端点击继续下载时，从上次断开的点继续读取
        # the_file = open(file_path, 'rb')
        # the_file.seek(start_bytes, os.SEEK_SET)
        #
        # # status=200表示下载开始，status=206表示下载暂停后继续，为了兼容火狐浏览器而区分两种状态
        # # 关于django的response对象，参考：https://www.cnblogs.com/scolia/p/5635546.html
        # # 关于response的状态码，参考：https://www.cnblogs.com/DeasonGuan/articles/Hanami.html
        # # FileResponse默认block_size = 4096，因此迭代器每次读取4KB数据
        # response = FileResponse(the_file, content_type=content_type, status=206 if start_bytes > 0 else 200)

        """ responds to the video file as """
        path = file_path
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
        range_match = range_re.match(range_header)
        try:
            size = os.path.getsize(path)
        except FileNotFoundError as e:
            return APIResponse(message='系统找不到指定的文件', code=404, http_status=404)
        content_type, encoding = mimetypes.guess_type(path)
        content_type = content_type or 'application/octet-stream'
        if range_match:
            first_byte, last_byte = range_match.groups()
            if first_byte:
                first_byte = int(first_byte)
            else:
                first_byte = 0
            last_byte = first_byte + 1024 * 1024 * 8  # 8M per piece, the maximum volume of the response body
            if last_byte > size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206,
                                         content_type=content_type)
            # 剩余待传输的文件字节长度
            resp['Content-Length'] = str(length)
            # 'Content-Range'的'/'之前描述响应覆盖的文件字节范围，起始下标为0，'/'之后描述整个文件长度，与'HTTP_RANGE'对应使用
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        else:
            # When the video stream is not obtained, the entire file is returned in the generator mode to save memory.
            resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
        resp['Accept-Ranges'] = 'bytes'
        # # 'Cache-Control'控制浏览器缓存行为，此处禁止浏览器缓存，参考：https://blog.csdn.net/cominglately/article/details/77685214
        # resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp


class AudioView(APIView):
    authentication_classes = (JwtTokenAuth,)

    permission_classes = [UserPermission, ViewPermission]

    def get(self, request):
        # 获取
        params = request.query_params
        device_id = params.get("device_id")
        if not device_id:
            return APIResponse(message='参数不合法', code=404, http_status=404)
        obj = AudioList.objects.get(device_id=device_id)
        serializer = AudioSerializer(obj)
        return APIResponse(result=serializer.data)

    # def post(self, request):
    #     # 添加
    #     serializer = AudioSerializer(data=request.data)
    #
    #     if serializer.is_valid():
    #         post = serializer.save()
    #
    #     return APIResponse(message='添加成功')

    def delete(self, request):
        # 删除
        device_id = request.data
        print(device_id)
        device_obj = AudioList.objects.get(id=device_id)
        if device_obj:
            device_obj.delete(
            )
            return APIResponse(message="删除成功")
        return APIResponse(code=500, message="删除失败，没找到该音频")

    def put(self, request):
        # 更新
        data = request.data
        serializer = AudioSerializer(data=request.data)
        if serializer.is_valid():
            device_id = data.get('id')
            del data['id']
            AudioList.objects.update_or_create(id=device_id, defaults=data)
        return APIResponse(code=200, message='更新成功')


class AudioListView(GenericViewSet, ListModelMixin):
    authentication_classes = (JwtTokenAuth,)
    permission_classes = [UserPermission, ViewPermission]
    queryset = AudioList.objects.all()
    serializer_class = AudioSerializer
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

    def _filter(self, request):
        params = request.query_params
        audio_id = params.get('id', None)
        name = params.get('name', None)
        file_path = params.get('file_path', None)
        device_id = params.get('device_id', None)

        queryset = self.filter_queryset(self.get_queryset())
        if audio_id:
            queryset = self.get_queryset().filter(id=audio_id)
        if name:
            queryset = self.get_queryset().filter(name__contains=name)
        if file_path:
            queryset = self.get_queryset().filter(file_path__contains=file_path)
        if device_id:
            queryset = self.get_queryset().filter(device_id=device_id)
        queryset = self.filter_queryset(queryset).order_by('-id')

        return queryset


class AudioChannelOpenView(APIView):
    authentication_classes = (JwtTokenAuth,)

    permission_classes = [UserPermission, ViewPermission]

    def post(self, request):
        # 打开
        device_id = request.data.get('device_id')
        device_ids = request.data.get('device_ids')
        try:
            device_obj = DeviceList.objects.get(id=device_id)
            if device_obj.status == DeviceStatusEnum.RECORDING.value:
                return APIResponse(code=400, message='录音通道已打开，请勿重复操作')
        except Exception as e:
            if not device_ids:
                return APIResponse(code=400, message='非法输入，设备不存在')

        if device_id:
            succeed = SgDeviceHelper.open_audio(device_obj)
            if succeed:
                return APIResponse(message='录音通道打开成功')
        elif device_ids:
            ids = ''
            if len(device_ids) == 1:
                ids += str(device_ids[0])
            else:
                for id in device_ids:
                    if isinstance(id, int):
                        ids += str(id) + ","
            if ids:
                device_objs = DeviceList.objects.extra(where=['id IN (' + ids + ')'])
                succeed_info = SgDeviceHelper().batch_open_audio(device_objs)
                print(succeed_info)
                if not succeed_info:
                    return APIResponse(code=400, message='批量开启录音通道失败')
                failed_info = filter(lambda pid: not succeed_info[pid], succeed_info)
                if len(list(failed_info)) == 0:
                    return APIResponse(message='批量开启录音通道成功')
                return APIResponse(message='部分设备录音通道打开成功')
        print(cache.RECORDING_DEVICES)

        return APIResponse(code=400, message='录音通道打开失败')


class AudioChannelCloseView(APIView):
    authentication_classes = (JwtTokenAuth,)

    permission_classes = [UserPermission, ViewPermission]

    def post(self, request):
        device_id = request.data.get('device_id')
        device_ids = request.data.get('device_ids')
        try:
            device_obj = DeviceList.objects.get(id=device_id)
            if device_obj.status == DeviceStatusEnum.RUNNING.value:
                return APIResponse(code=400, message='录音通道已关闭，请勿重复操作')
        except Exception as e:
            if not device_ids:
                return APIResponse(code=400, message='非法输入，设备不存在')
        device_objs = []
        if device_id:
            device_objs = [device_obj]
        elif device_ids:
            ids = ''
            if len(device_ids) == 1:
                ids += str(device_ids[0])
            else:
                for id in device_ids:
                    if isinstance(id, int):
                        ids += str(id) + ","
            if ids:
                device_objs = DeviceList.objects.extra(where=['id IN (' + ids + ')']).all()
        success_list = []

        for device_obj in device_objs:
            checked, info = SgDeviceHelper.check_recording_device(device_obj.ip_addr)
            if checked:
                succeed, data = SgDeviceHelper.close_audio(device_obj)
                if succeed:
                    AudioList.objects.create(**data)
                    # 获取保存的文件名,大小,时长，写入数据库
                    message = '录音通道关闭成功,音频大小:{}M，路径:{},时长：{}s'.format(
                        data['file_size'], data['file_path'], data['duration'])
                    device_obj.save()
                    if len(device_objs) == 1:
                        return APIResponse(message=message)
                    else:
                        success_list.append(device_obj.id)
        if len(success_list) == 0:
            return APIResponse(code=400, message='录音通道关闭失败')
        else:
            return APIResponse(message='录音通道关闭成功')
