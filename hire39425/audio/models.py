from datetime import datetime

from django.db import models

# Create your models here.
from device.models import DeviceList


class AudioList(models.Model):
    device = models.ForeignKey(DeviceList, related_name='audios', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=64, null=True, verbose_name="名称")
    file_path = models.CharField(max_length=128, null=True, verbose_name="文件路径")
    file_size = models.FloatField(max_length=12, null=True, default=0, verbose_name="文件大小")
    duration = models.IntegerField(null=True, verbose_name="时长")
    status = models.IntegerField(default=1, verbose_name="状态")
    deleted = models.IntegerField(default=0)
    describe = models.TextField(null=True, verbose_name="描述", blank=True)
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Mata:
        app_label = "audio"

    @property
    def device_name(self):
        return self.device.device_name if self.device else ''
