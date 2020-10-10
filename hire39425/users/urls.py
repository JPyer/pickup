from django.conf.urls import url
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework_jwt.views import obtain_jwt_token
from users import views

# csrf_exempt  跨域访问，test
from users.views import UserRouteView, UserRoleView, UserInfoView, LogoutView, OrganizationListView, \
    OrganizationUserListView, OrganizationView, OrganizationUserView, ModifyPasswordView, UserPermissionView

urlpatterns = [
    # 登录接口
    url('auth/login', csrf_exempt(views.LoginView.as_view())),
    # url(r'auth/login', csrf_exempt(obtain_jwt_token)),
    url('user/routes/$', UserRouteView.as_view(), name="user_routes"),
    path('user/info', UserInfoView.as_view(), name="user_info"),
    path('user/permission', UserPermissionView.as_view(), name="user_permission_info"),
    path('user/password/modify', ModifyPasswordView.as_view(), name="user_passwd_modify"),
    path('role', UserRoleView.as_view(), name="user_role"),
    path('auth/logout', LogoutView.as_view(), name="logout"),
    path('organization', OrganizationView.as_view(), name="org"),
    path('organization/list', OrganizationListView.as_view({"get": "list"}), name="org_list"),
    path('organization/user', OrganizationUserView.as_view(), name="org_user"),
    path('organization/user/list', OrganizationUserListView.as_view({"get": "list"}), name="org_user_list")
]
