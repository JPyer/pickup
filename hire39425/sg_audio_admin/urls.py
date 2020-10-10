from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers


from users.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('users.urls')),
    path('api/', include('device.urls')),
    path('api/', include('audio.urls')),
    path('api/', include('system.urls'))
]
