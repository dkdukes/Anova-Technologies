from django.urls import path

from .views import (
    CreateOrderView,
    DeliveryFeeView,
    AdminOrderListAPIView,
    AdminOrderDetailAPIView,
)


urlpatterns = [
    # Customer order endpoints
    path(
        "create/",
        CreateOrderView.as_view(),
        name="create-order",
    ),

    path(
        "delivery-fee/",
        DeliveryFeeView.as_view(),
        name="delivery-fee",
    ),

    # Admin order endpoints
    path(
        "admin/",
        AdminOrderListAPIView.as_view(),
        name="admin-order-list",
    ),

    path(
        "admin/<int:pk>/",
        AdminOrderDetailAPIView.as_view(),
        name="admin-order-detail",
    ),
]