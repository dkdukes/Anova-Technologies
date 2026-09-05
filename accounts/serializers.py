from rest_framework import serializers
from .models import CustomUser


class AdminCustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "profile_image",
            "order_count",
            "total_spent",
            "created_at",
            "updated_at",
        )

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()

        return full_name or obj.username

    def get_order_count(self, obj):
        return obj.orders.count()

    def get_total_spent(self, obj):
        from django.db.models import Sum

        total = obj.orders.filter(
            payment_status="paid"
        ).aggregate(
            total=Sum("total")
        )["total"]

        return total or 0