import datetime

import pytz
from django.core.cache import cache

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
from rest_framework.authentication import TokenAuthentication, BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


class JwtTokenAuth():
    def authenticate(self, request):
        token = {"token": None}
        # print(request.META.get("HTTP_TOKEN"))
        http_authentication = request.META.get('HTTP_AUTHENTICATION')
        if http_authentication:
            token["token"] = request.META.get('HTTP_AUTHENTICATION').split("Token ")[1]
            valid_data = VerifyJSONWebTokenSerializer().validate(token)
            user = valid_data['user']
            if user:
                return
            else:
                raise AuthenticationFailed('认证失败')
        else:
            raise AuthenticationFailed('认证失败')

    def authenticate_header(self, request):
        return 'Token'