#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import datetime
import os
import sys

from utils import exec_backend_process
from utils.sg_device_helper import SgDeviceHelper
import cache


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sg_audio_admin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    args = sys.argv
    if len(args) > 1 and args[1] == 'runserver':
        # online_device_list = SgDeviceHelper.search_device()
        # # cache.ONLINE_DEVICE_LIST = online_device_list
        # cache.CurDevices.set_devices(online_device_list)
        exec_backend_process('loop_search_device', SgDeviceHelper().loop_search_device)

        cache.START_RUNNING_TIME = datetime.datetime.now()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
