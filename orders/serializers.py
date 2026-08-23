from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = (
            "product",
            "product_name",
            "sku",
            "quantity",
            "unit_price",
            "total_price",
        )


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "full_name",
            "email",
            "phone",
            "county",
            "town",
            "delivery_address",
            "payment_method",
            "payment_status",
            "status",
            "subtotal",
            "delivery_fee",
            "total",
            "items",
            "created_at",
        )