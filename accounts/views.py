from rest_framework import generics, filters

from .models import CustomUser
from .serializers import AdminCustomerSerializer


class AdminCustomerListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_by("-created_at")

    serializer_class = AdminCustomerSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    ]

    ordering_fields = [
        "username",
        "email",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]


class AdminCustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()

    serializer_class = AdminCustomerSerializer