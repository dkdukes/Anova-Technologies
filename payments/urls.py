from django.urls import path

from .views import (
    MpesaTestView,
    MpesaStkTestView,
    MpesaCallbackView,
    MpesaPaymentStatusView
)


urlpatterns = [
    path(
        "test/",
        MpesaTestView.as_view(),
        name="mpesa-test",
    ),

    path(
        "stk-test/",
        MpesaStkTestView.as_view(),
        name="mpesa-stk-test",
    ),
      path(
        "mpesa/callback/",
        MpesaCallbackView.as_view(),
        name="mpesa-callback",
    ),

    path(
    "mpesa/status/<str:checkout_request_id>/",
    MpesaPaymentStatusView.as_view(),
    name="mpesa-payment-status",
),
]