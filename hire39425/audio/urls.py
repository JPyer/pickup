from django.urls import include, path
from rest_framework import routers

from audio.views import AudioView, AudioFileView, AudioListView, AudioChannelOpenView, AudioChannelCloseView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('audio', AudioView.as_view(), name="audio_api"),
    path('audio/play', AudioFileView.as_view(), name="audio_play_api"),
    path('audio/list', AudioListView.as_view({"get": "list"}), name="audio_info_list"),
    path('audio/channel/open', AudioChannelOpenView.as_view(), name="audio_open"),
    path('audio/channel/close', AudioChannelCloseView.as_view(), name="audio_close")
]
