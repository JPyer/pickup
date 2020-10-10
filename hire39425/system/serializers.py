# encoding:utf-8

from rest_framework import serializers

from system.models import SystemMessage


class SysMsgSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SystemMessage
        fields = ['id', 'content', 'gmt_create']

        # extra_kwargs = {
        #     'test': {'write_only': True}
        # }
