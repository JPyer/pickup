# encoding:utf-8

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from device.models import DeviceList, DeviceGroup


class DeviceSerializer(serializers.ModelSerializer):
    # gmt_modify = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)

    class Meta:
        model = DeviceList
        fields = ['id', 'device_id', 'product_id', 'group_name',
                  'device_group_id', 'device_name', 'status','audio_count',
                  'ip_addr', 'mac_addr', 'gmt_create', 'gmt_modify']

        extra_kwargs = {
            'product_id': {'validators': [UniqueValidator(
                queryset=model.objects.all(),
                message='产品ID重复')]},
            'ip_addr': {'validators': [UniqueValidator(
                queryset=model.objects.all(),
                message='IP地址重复')]},
        }


class DeviceAudioChannelSerializer(serializers.ModelSerializer):
    """音频通道设置"""

    class Meta:
        model = DeviceList
        fields = ['id', 'output_channel', 'audio_sample_rate', 'audio_sample_bits', 'retrans_timeout']


class DeviceAudioSetSerializer(serializers.ModelSerializer):
    """音频参数设置"""

    class Meta:
        model = DeviceList
        fields = ['id', 'status', 'fft_points', 'output_gain', 'mic_direction']


class DeviceGroupSerializer(serializers.ModelSerializer):
    """设备分组设置"""

    class Meta:
        model = DeviceGroup
        fields = ['id', 'name', 'device_count']
