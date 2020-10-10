# encoding:utf-8

from rest_framework import serializers

from audio.models import AudioList


class AudioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AudioList
        fields = ['id', 'name', 'device_name', 'file_path',  'file_size', 'duration', 'gmt_create']
        read_only_fields = ('file_path', 'device_name')
        # extra_kwargs = {
        #     'test': {'write_only': True}
        # }