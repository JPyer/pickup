from datetime import datetime

from django.db import models

# Create your models here.
from users.models import User
from utils.constant import SYSTEM_MSG_TYPE_CHOICES


class SystemInfo(models.Model):
    firmware_version = models.CharField(max_length=12, null=True, blank=True, verbose_name="固件版本")
    software_version = models.CharField(max_length=12, null=True, blank=True, verbose_name="软件版本")

    class Meta:
        app_label = 'system'


class SystemUpgradeRecord(models.Model):
    version = models.CharField(max_length=12, null=True, blank=True, verbose_name="升级版本")
    firmware_version = models.CharField(max_length=12, null=True, blank=True, verbose_name="固件版本")
    software_version = models.CharField(max_length=12, null=True, blank=True, verbose_name="软件版本")
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="升级时间")

    class Meta:
        app_label = 'system'


class SystemMessage(models.Model):
    content = models.CharField(max_length=255, null=True, blank=True, verbose_name="消息内容")
    gmt_create = models.DateTimeField(default=datetime.now, verbose_name="创建时间")
    unread = models.BooleanField(default=True, verbose_name="未读")
    msg_type = models.IntegerField(default=1, verbose_name="消息类型", choices=SYSTEM_MSG_TYPE_CHOICES)

    class Meta:
        app_label = 'system'
