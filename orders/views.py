from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer
from decimal import Decimal


def get_delivery_fee(county):
    """
    Return the delivery fee based on the
    customer's county.
    """

    delivery_fees = {
        "Nairobi": Decimal("300.00"),
        "Kiambu": Decimal("400.00"),
        "Machakos": Decimal("450.00"),
        "Kajiado": Decimal("450.00"),
        "Nakuru": Decimal("500.00"),
        "Murang'a": Decimal("450.00"),
        "Nyeri": Decimal("500.00"),
        "Kirinyaga": Decimal("500.00"),
        "Mombasa": Decimal("700.00"),
        "Kilifi": Decimal("750.00"),
        "Kwale": Decimal("750.00"),
        "Kisumu": Decimal("600.00"),
        "Siaya": Decimal("600.00"),
        "Kakamega": Decimal("600.00"),
        "Bungoma": Decimal("600.00"),
        "Uasin Gishu": Decimal("600.00"),
    }

    return delivery_fees.get(
        county,
        Decimal("500.00"),
    )

class CreateOrderView(APIView):

    @transaction.atomic
    def post(self, request):

        customer = request.data.get("customer", {})
        delivery = request.data.get("delivery", {})
        items = request.data.get("items", [])
        payment_method = request.data.get(
            "payment_method",
            "mpesa",
        )

        # -----------------------------------------
        # Validate customer information
        # -----------------------------------------

        full_name = customer.get("full_name", "").strip()
        email = customer.get("email", "").strip()
        phone = customer.get("phone", "").strip()

        if not full_name:
            return Response(
                {"error": "Full name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not phone:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------
        # Validate delivery information
        # -----------------------------------------

        county = delivery.get("county", "").strip()
        town = delivery.get("town", "").strip()
        address = delivery.get("address", "").strip()

        if not county:
            return Response(
                {"error": "County is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not town:
            return Response(
                {"error": "Town is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not address:
            return Response(
                {"error": "Delivery address is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------
        # Validate items
        # -----------------------------------------

        if not items:
            return Response(
                {"error": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment_method not in {
            "mpesa",
            "card",
            "cod",
        }:
            return Response(
                {"error": "Invalid payment method."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------
        # Create temporary order data
        # -----------------------------------------

        order_items = []
        subtotal = Decimal("0.00")

        for item in items:

            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id:
                return Response(
                    {"error": "Product ID is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return Response(
                    {"error": "Invalid quantity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -------------------------------------
            # Lock product row while checking stock
            # -------------------------------------

            try:
                product = (
                    Product.objects
                    .select_for_update()
                    .get(
                        id=product_id,
                        status="active",
                    )
                )
            except Product.DoesNotExist:
                return Response(
                    {
                        "error": (
                            f"Product {product_id} "
                            "does not exist or is unavailable."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -------------------------------------
            # Check stock
            # -------------------------------------

            if product.stock_quantity < quantity:
                return Response(
                    {
                        "error": (
                            f"Only {product.stock_quantity} "
                            f"units of {product.name} are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -------------------------------------
            # Get price from database
            # -------------------------------------

            unit_price = product.current_price

            item_total = unit_price * quantity

            subtotal += item_total

            order_items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": item_total,
                }
            )

        # -----------------------------------------
        # Delivery fee
        # -----------------------------------------

        # Temporary flat delivery fee.
        # We'll make this location-based later.
        delivery_fee = get_delivery_fee(county)

        total = subtotal + delivery_fee

        # -----------------------------------------
        # Create order
        # -----------------------------------------

        order = Order.objects.create(
            user=(
                request.user
                if request.user.is_authenticated
                else None
            ),
            full_name=full_name,
            email=email,
            phone=phone,
            county=county,
            town=town,
            delivery_address=address,
            payment_method=payment_method,
            payment_status="pending",
            status="pending",
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
        )

        # -----------------------------------------
        # Create order items
        # -----------------------------------------

        for item in order_items:

            product = item["product"]

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                sku=product.sku,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
            )

        # -----------------------------------------
        # Return created order
        # -----------------------------------------

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )