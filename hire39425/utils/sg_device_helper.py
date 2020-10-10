# encoding:utf-8
import datetime
import json
import os
import re
import subprocess
import sys
import time

import cache
from sg_code.sg_search import sg_search_main
from utils import runcmd, kill_pid, DaemonProcess, exec_backend_process
from utils.constant import SG_SOFTWARE_PATH, SG_AUDIO_PATH, DeviceStatusEnum, SG_DEVICE_FILE


class SgDeviceHelper:
    """后端调用设备接口统一入口"""

    def __init__(self):
        pass

    @staticmethod
    def search_device(product_ids=None, search_ip_addr=None):
        device_list = []
        try:
            success, device_list = sg_search_main(product_ids=product_ids, search_ip_addr=search_ip_addr)

        except Exception as e:
            print(e)
        return device_list

    def loop_search_device(self, wait=60):
        """循环查找设备"""
        while True:
            online_device_list = self.search_device()
            cache.CurDevices.set_devices(online_device_list)
            time.sleep(wait)

    @staticmethod
    def check_recording_device(ip_addr):
        pid_file = os.path.join(SG_SOFTWARE_PATH, 'pid.txt')
        with open(pid_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                if ip_addr in line:
                    return True, line
        return False, None

    def set_audio(self, info):
        """设置音频参数"""

    def set_audio_channel(self, info):
        """设置音频通道"""

    @staticmethod
    def open_audio(device_obj, duration=60 * 60 * 24):
        """开始录音"""
        # 录音文件名
        localtime = time.strftime("-D%Y%m%dT%H%M%S", time.localtime())
        file_name = "[{}]{}-{}k-{}ch-{}bit.pcm".format(
            re.sub(r'[\\/:\*\?"<>|]', '_', device_obj.device_name),
            localtime,
            device_obj.audio_sample_rate // 1000,
            1,  # 音频声道数
            device_obj.audio_sample_bits
        )

        print(cache.RECORDING_DEVICES)

        script_path = os.path.join(SG_SOFTWARE_PATH, 'sg_audio.py')
        os.chdir(SG_SOFTWARE_PATH)
        cmd = 'python38 {} {} -d {} '.format('sg_audio.py', device_obj.ip_addr, duration)

        cmd += '--fp {}'.format(file_name)

        pid, ppid = exec_backend_process("open_audio_{}".format(device_obj.id), runcmd, cmd)
        time.sleep(4)
        checked, info = SgDeviceHelper.check_recording_device(device_obj.ip_addr)
        if checked:
            device_obj.status = DeviceStatusEnum.RECORDING.value
            device_obj.save()
            cache.RECORDING_DEVICES[device_obj.id] = {
                "pid": info.split(":")[1],
                "filename": file_name,
                "start_time": datetime.datetime.now()
            }
            print(cache.RECORDING_DEVICES[device_obj.id])
            return True
        return False

    @staticmethod
    def close_audio(device_obj, pid=None):
        """结束录音"""
        succeed = False
        data = {}
        # TODO 目前手动杀进程
        cache_audio_info = cache.RECORDING_DEVICES[device_obj.id]
        if not pid:
            pid = cache.RECORDING_DEVICES.get(device_obj.id)['pid']
        if pid:
            succeed = kill_pid(pid)
        if not succeed:
            return False, data
        device_obj.status = DeviceStatusEnum.RUNNING.value
        # TODO
        data = {
            'device_id': device_obj.id,
            'file_path': cache_audio_info['filename'],
            'duration': (datetime.datetime.now() - cache_audio_info['start_time']).seconds,
            'file_size': SgDeviceHelper.get_file_size(cache_audio_info['filename'], 'M')
        }
        return succeed, data

    def batch_open_audio(self, device_objs):
        """批量开启录音"""
        result = {}
        # map(lambda obj: result.update({obj.id: self.open_audio(obj)}), device_objs)
        obj = device_objs[0]
        result.update({obj.id: self.open_audio(obj)})
        return result

    def batch_close_audio(self, pids):
        """批量结束录音"""
        map(lambda pid: self.close_audio(pid), pids)

    @staticmethod
    def get_file_size(filename, unit='M'):
        file_path = os.path.join(SG_AUDIO_PATH, filename)
        fsize = os.path.getsize(file_path)
        if unit == 'M':
            fsize = round(fsize / float(1024 * 1024), 2)
        else:
            fsize = round(fsize / float(1024))

        return round(fsize, 2)
