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



# =========================================================
# ADMIN ORDER SERIALIZERS
# =========================================================

class AdminOrderItemSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "sku",
            "quantity",
            "unit_price",
            "total_price",
        )


class AdminOrderSerializer(serializers.ModelSerializer):

    items = AdminOrderItemSerializer(
        many=True,
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    payment_status_display = serializers.CharField(
        source="get_payment_status_display",
        read_only=True,
    )

    payment_method_display = serializers.CharField(
        source="get_payment_method_display",
        read_only=True,
    )

    class Meta:
        model = Order

        fields = (
            "id",
            "order_number",

            # Customer
            "user",
            "full_name",
            "email",
            "phone",

            # Delivery
            "county",
            "town",
            "delivery_address",

            # Payment
            "payment_method",
            "payment_method_display",
            "payment_status",
            "payment_status_display",

            # Order status
            "status",
            "status_display",

            # Money
            "subtotal",
            "delivery_fee",
            "total",

            # Other
            "notes",
            "items",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "user",
            "created_at",
            "updated_at",
        )