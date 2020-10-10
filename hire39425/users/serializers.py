# encoding:utf-8


from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator, BaseUniqueForValidator, UniqueTogetherValidator
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from users.models import User, UserRole


def is_required(name):
    if not name:
        raise ValidationError('不能为空')
    else:
        return name


class LoginSerializer(JSONWebTokenSerializer):
    class Meta:
        model = User
        fields = ['role_id', 'username', 'password', 'is_active']


class AuthUserSerializer(serializers.Serializer):
    username = serializers.CharField(label='用户名', max_length=64, help_text='用户名',
                                     validators=[
                                         UniqueValidator(
                                             queryset=User.objects.all(),
                                             message="该用户名已存在"
                                         )
                                     ])
    password = serializers.CharField(label='密码', max_length=16, help_text='登录密码',
                                     validators=[
                                         is_required
                                     ])

    class Meta:
        model = User
        fields = ['role_id', 'username', 'realname', 'telephone', 'password', 'is_active']

    def validate_username(self, value):
        """

        :return:
        """
        if not str(value):
            raise serializers.ErrorDetail(string='用户名不能为空')
        else:
            return value

    def get_role(self, role):
        return UserRole.objects.get(uid=role).id


class ModifyPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(label='旧密码', min_length=6, max_length=32, help_text='旧登录密码',
                                         validators=[
                                             is_required
                                         ])
    password = serializers.CharField(label='密码', min_length=6, max_length=32, help_text='登录密码',
                                     validators=[
                                         is_required
                                     ])
    re_password = serializers.CharField(label='确认密码', min_length=6, max_length=32, help_text='确认密码',
                                        validators=[
                                            is_required
                                        ])

    class Meta:
        model = User
        fields = ['old_password', 'password', 're_password']


class UserSerializer(serializers.ModelSerializer):
    # active = serializers.BooleanField(source='is_active')
    class Meta:
        model = User
        fields = ['id', 'username', 'realname', 'telephone', 'last_login', 'date_joined', 'is_active']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'realname', 'telephone', 'last_login', 'date_joined', 'is_active']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role_uid', 'realname', 'telephone', 'last_login', 'date_joined', 'is_active']


class OrganizationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role_uid', 'realname', 'telephone', 'last_login', 'date_joined', 'is_active']
