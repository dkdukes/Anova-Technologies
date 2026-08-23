from django.urls import path

from .views import MpesaTestView


urlpatterns = [
    path(
        "test/",
        MpesaTestView.as_view(),
        name="mpesa-test",
    ),
]