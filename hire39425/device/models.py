import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
from utils.constant import DEVICE_STATUS_CHOICES


class DeviceGroup(models.Model):
    """组名"""
    name = models.CharField(verbose_name='组名', max_length=32, null=False)

    class Meta:
        app_label = 'device'

    def __str__(self):
        return self.name

    def device_count(self):
        return self.devices.count()


class DeviceList(models.Model):
    """设备列表"""
    device_id = models.CharField(verbose_name='设备id', max_length=32, null=True)
    device_group = models.ForeignKey(DeviceGroup, related_name='devices', on_delete=models.SET_NULL, null=True)
    device_name = models.CharField(verbose_name='设备名', max_length=64, null=True)
    product_id = models.CharField(verbose_name='产品ID', max_length=64, null=True, unique=True)
    ip_addr = models.CharField(verbose_name='设备IP', max_length=16, null=True)
    mac_addr = models.CharField(verbose_name='网卡物理地址', max_length=64, null=True)
    port = models.CharField(verbose_name='设备端口号', max_length=8, null=True)
    security_key = models.CharField(verbose_name='设备密钥', max_length=64, null=True)
    status = models.IntegerField(verbose_name='状态', default=1, choices=DEVICE_STATUS_CHOICES)
    dns_server1 = models.CharField(max_length=16, verbose_name='dns server 1', null=True)
    dns_server2 = models.CharField(max_length=16, verbose_name='dns server 2', null=True)
    device_position = models.CharField(max_length=100, verbose_name='设备位置', null=True)
    gmt_create = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    gmt_modify = models.DateTimeField(default=timezone.now, verbose_name='更新时间')
    remarks = models.CharField(max_length=100, verbose_name='备注', null=True)

    fw_ver = models.CharField(max_length=64, verbose_name="固件版本", null=True)
    sw_ver = models.CharField(max_length=64, verbose_name="软件版本", null=True)
    running_time = models.TimeField(verbose_name="运行时间", null=True)

    # 音频参数设置
    fft_points = models.IntegerField(verbose_name='FFT点数参数', null=True)
    output_gain = models.IntegerField(verbose_name='输出增益参数', default=8, null=True)
    mic_direction = models.CharField(verbose_name='麦克风头指向参数', max_length=32, null=True)

    # 音频通道参数
    output_channel = models.IntegerField(verbose_name='音频输出通道编号', null=True)
    # audio_encoder = models.IntegerField(verbose_name='编码器ID', null=True, default=3)
    # audio_channels = models.IntegerField(verbose_name='音频声道数', null=True, default=1)
    audio_sample_rate = models.IntegerField(verbose_name='音频采样率', null=True, default=16000)
    audio_sample_bits = models.IntegerField(verbose_name='采样位数', null=True, default=24)
    # audio_frame_size = models.IntegerField(verbose_name='音频帧长', null=True, default=320)
    # audio_bitrate = models.IntegerField(verbose_name='音频编码器比特率', null=True)
    retrans_timeout = models.IntegerField(verbose_name='重传超时阈值', null=True, default=1000)

    def __str__(self):
        return "%s %s " % (self.device_id, self.device_name)

    def audio_count(self):
        return self.audios.count()

    @property
    def group_name(self):
        return self.device_group.name if self.device_group_id else ''

    class Meta:
        app_label = 'device'


class DeviceSysInfo(models.Model):
    table_name = 'device_sys_info'
    gmt_create = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    gmt_modify = models.DateTimeField(default=timezone.now, verbose_name="更新时间")

    class Mata:
        app_label = "device"

    @classmethod
    def get_storage_info(cls):
        "存储信息"
        return "100M"

    @classmethod
    def get_online_devices(cls):
        return 5

    @classmethod
    def get_offline_device(cls):
        return 10
