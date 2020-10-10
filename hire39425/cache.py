# encoding:utf-8
import json
import os

from utils.constant import SG_DEVICE_FILE, DeviceStatusEnum

ONLINE_DEVICE_LIST = []
START_RUNNING_TIME = None
RUNNING_SECONDS = 0
RECORDING_DEVICES = {}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sg_audio_admin.settings")
import django

django.setup()
from device.models import DeviceList


class CurrentDevices(object):

    def __init__(self):
        self.devices = []

    def get_device_list(self):
        with open(SG_DEVICE_FILE, "r") as f:
            self.devices = json.loads(f.read())
        return self.devices

    def set_devices(self, device_list):
        history_device_list = self.get_device_list()
        self.devices = device_list or []
        device_product_ids = [d['product_id'] for d in self.devices]
        history_device_product_ids = []
        if history_device_list:
            history_device_product_ids = [d['product_id'] for d in history_device_list]

            stopped_devices = list(set(history_device_product_ids).difference(set(device_product_ids)))
            if stopped_devices:
                from system.models import SystemMessage
                content = "发现掉线设备:{}".format(",".join([d for d in stopped_devices]))
                SystemMessage.objects.create(**{"content": content, "unread": 1})

        if device_list:
            status = DeviceStatusEnum.RUNNING.value
            update_product_ids = device_product_ids
        else:
            status = DeviceStatusEnum.STOP.value
            update_product_ids = history_device_product_ids

        if update_product_ids:
            DeviceList.objects.filter(product_id__in=update_product_ids).update(status=status)

        with open(SG_DEVICE_FILE, "w") as f:
            f.write(json.dumps(device_list))


CurDevices = CurrentDevices()
