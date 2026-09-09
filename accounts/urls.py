
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    RegisterAPIView,
    AdminCustomerListAPIView,
    AdminCustomerDetailAPIView,
    LoginAPIView
)


urlpatterns = [
    # User registration
    path(
        "auth/register/",
        RegisterAPIView.as_view(),
        name="register",
    ),

    # User login
    path(
        "auth/login/",
        LoginAPIView.as_view(),
        name="login",
    ),

    # Refresh access token
    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # Admin customers
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
]

