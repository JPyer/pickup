from django.urls import include, path
from rest_framework import routers

from device.views import DeviceViewSet, DeviceView, DeviceListView, DeviceGroupView, DeviceGroupListView, \
    DeviceDiscoveryView, DeviceAudioChannelView, DeviceAudioSetView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('device', DeviceView.as_view(), name="device_api"),
    path('device/discovery', DeviceDiscoveryView.as_view(), name="device_discovery_api"),
    path('device/list', DeviceListView.as_view({"get": "list"}), name="device_info_list"),
    path('device/group', DeviceGroupView.as_view(), name="device_group"),
    path('device/group/list', DeviceGroupListView.as_view({"get": "list"}), name="device_group_list"),
    path('device/group/option', DeviceGroupListView.as_view({"get": "options"}), name="device_group_options"),
    path('device/option', DeviceListView.as_view({"get": "options"}), name="device_options"),
    path('device/audio/channel', DeviceAudioChannelView.as_view(), name="device_audio_channel"),
    path('device/audio', DeviceAudioSetView.as_view(), name="device_audio"),
]
