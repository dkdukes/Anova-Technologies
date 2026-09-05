from django.urls import path

from .views import (
    AdminCustomerListAPIView,
    AdminCustomerDetailAPIView,
)


urlpatterns = [
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