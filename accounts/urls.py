from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    RegisterAPIView,
    AdminCustomerListAPIView,
    AdminCustomerDetailAPIView,
    AdminCreateUserAPIView,
    LoginAPIView,
    AdminUserListAPIView,
    AdminUserDetailAPIView,
    AdminUserStatusAPIView,
    AdminUserPasswordAPIView
)


urlpatterns = [
    # -------------------------------------------------
    # USER REGISTRATION
    # -------------------------------------------------

    path(
        "auth/register/",
        RegisterAPIView.as_view(),
        name="register",
    ),

    # -------------------------------------------------
    # USER LOGIN
    # -------------------------------------------------

    path(
        "auth/login/",
        LoginAPIView.as_view(),
        name="login",
    ),

    # -------------------------------------------------
    # REFRESH ACCESS TOKEN
    # -------------------------------------------------

    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # -------------------------------------------------
    # ADMIN CUSTOMERS
    # -------------------------------------------------

    path(
        "admin/",
        AdminCustomerListAPIView.as_view(),
        name="admin-customer-list",
    ),

    path(
        "admin/<int:pk>/",
        AdminCustomerDetailAPIView.as_view(),
        name="admin-customer-detail",
    ),

    # -------------------------------------------------
    # ADMIN CREATE STAFF / ADMIN
    # -------------------------------------------------

    path(
        "admin/create/",
        AdminCreateUserAPIView.as_view(),
        name="admin-create-user",
    ),

    # Staff / Admin management

    path(
        "admin/users/",
        AdminUserListAPIView.as_view(),
        name="admin-user-list",
    ),

    path(
        "admin/users/<int:pk>/",
        AdminUserDetailAPIView.as_view(),
        name="admin-user-detail",
    ),

    path(
        "admin/users/<int:pk>/status/",
        AdminUserStatusAPIView.as_view(),
        name="admin-user-status",
    ),

    path(
        "admin/users/<int:pk>/password/",
        AdminUserPasswordAPIView.as_view(),
        name="admin-user-password",
    ),
]