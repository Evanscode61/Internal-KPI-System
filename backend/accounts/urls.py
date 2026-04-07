from django.urls import path
from .views import (user_login_view, token_refresh_view, user_logout_view, create_user_view,
                    register_user_view, create_role, delete_role_view, list_users_view, update_user_view,
                    update_role_view, delete_user_view, reset_password_view, view_user_profile, list_roles_view,
                    request_otp_view, assign_role_view, my_profile_view, upload_profile_picture_view,
                    delete_profile_picture_view)

urlpatterns = [
    path("login/", user_login_view ,name="login"),
    path("refresh/", token_refresh_view , name="refresh"),
    path("logout/", user_logout_view , name = "logout"),
    path("reset_password/", reset_password_view, name="reset_password"),
    path("create_user/", create_user_view, name = "create_user"),
    path("register_user/", register_user_view, name="register"),
    path('user/profile/<str:user_uuid>/', view_user_profile, name='view_user_profile'),
    path("list_users/", list_users_view, name="list_user" ),
    path("delete_user/<user_uuid>/", delete_user_view, name="delete_user_view"),
    path("update_user/<str:user_uuid>/", update_user_view, name="update_user"),
    path("otp/request/", request_otp_view, name="request_otp"),
    path('profile/me/',              my_profile_view,              name='my_profile'),
    path('profile/picture/upload/',  upload_profile_picture_view,  name='upload_picture'),
    path('profile/picture/delete/',  delete_profile_picture_view,  name='delete_picture'),

#------------------------------------------------------------------------------
# ROLES URL
#-----------------------------------------------------------------------------

    path("role/update/<str:name>/", update_role_view, name="update_role"),
    path("role/create/", create_role, name="create_role"),
    path("role/delete/<str:name>/",delete_role_view, name="delete_role"),
    path("role/list/", list_roles_view, name="list_roles"),
    path("role/assign/", assign_role_view, name="assign_role"),


]
