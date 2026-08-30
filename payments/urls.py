from django.urls import path

from .views import (
    MpesaTestView,
    MpesaStkTestView,
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
]