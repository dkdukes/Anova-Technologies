from django.urls import path

from .views import CreateOrderView, DeliveryFeeView


urlpatterns = [
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
]