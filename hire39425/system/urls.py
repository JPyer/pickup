from django.urls import include, path
from rest_framework import routers

from system.views import SystemInfoView, SystemMsgView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('system/info', SystemInfoView.as_view(), name="sys_info_api"),
    path('system/message', SystemMsgView.as_view({'get': 'list'}), name="sys_msg_api"),
]
