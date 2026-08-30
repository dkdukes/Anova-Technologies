from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer
from decimal import Decimal
from payments.models import Payment
from payments.mpesa import MpesaService


def get_delivery_fee(county):
    delivery_fees = {
        "baringo": Decimal("550.00"),
        "bomet": Decimal("550.00"),
        "bungoma": Decimal("600.00"),
        "busia": Decimal("600.00"),
        "elgeyo-marakwet": Decimal("600.00"),
        "embu": Decimal("500.00"),
        "garissa": Decimal("650.00"),
        "homa bay": Decimal("650.00"),
        "isiolo": Decimal("600.00"),
        "kajiado": Decimal("450.00"),
        "kakamega": Decimal("600.00"),
        "kericho": Decimal("550.00"),
        "kiambu": Decimal("400.00"),
        "kilifi": Decimal("750.00"),
        "kirinyaga": Decimal("500.00"),
        "kisii": Decimal("600.00"),
        "kisumu": Decimal("600.00"),
        "kitui": Decimal("550.00"),
        "kwale": Decimal("750.00"),
        "laikipia": Decimal("550.00"),
        "lamu": Decimal("800.00"),
        "machakos": Decimal("450.00"),
        "makueni": Decimal("500.00"),
        "mandera": Decimal("900.00"),
        "marsabit": Decimal("800.00"),
        "meru": Decimal("550.00"),
        "migori": Decimal("650.00"),
        "mombasa": Decimal("700.00"),
        "murang'a": Decimal("450.00"),
        "nairobi": Decimal("300.00"),
        "nakuru": Decimal("500.00"),
        "nandi": Decimal("550.00"),
        "narok": Decimal("600.00"),
        "nyamira": Decimal("600.00"),
        "nyandarua": Decimal("500.00"),
        "nyeri": Decimal("500.00"),
        "samburu": Decimal("700.00"),
        "siaya": Decimal("600.00"),
        "taita-taveta": Decimal("750.00"),
        "tana river": Decimal("750.00"),
        "tharaka-nithi": Decimal("550.00"),
        "trans nzoia": Decimal("600.00"),
        "turkana": Decimal("850.00"),
        "uasin gishu": Decimal("600.00"),
        "vihiga": Decimal("600.00"),
        "wajir": Decimal("850.00"),
        "west pokot": Decimal("650.00"),
    }

    # Normalize the value coming from the request
    normalized_county = county.strip().lower()

    return delivery_fees.get(
        normalized_county,
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

        full_name = customer.get(
            "full_name",
            ""
        ).strip()

        email = customer.get(
            "email",
            ""
        ).strip()

        phone = customer.get(
            "phone",
            ""
        ).strip()

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

        county = delivery.get(
            "county",
            ""
        ).strip()

        town = delivery.get(
            "town",
            ""
        ).strip()

        address = delivery.get(
            "address",
            ""
        ).strip()

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
        # Prepare order items
        # -----------------------------------------

        order_items = []

        subtotal = Decimal("0.00")

        for item in items:

            product_id = item.get(
                "product_id"
            )

            quantity = item.get(
                "quantity"
            )

            if not product_id:
                return Response(
                    {
                        "error":
                        "Product ID is required."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                quantity = int(quantity)

            except (
                TypeError,
                ValueError,
            ):
                return Response(
                    {
                        "error":
                        "Invalid quantity."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if quantity <= 0:
                return Response(
                    {
                        "error":
                        "Quantity must be greater than zero."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -------------------------------------
            # Lock product
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
                            f"Only "
                            f"{product.stock_quantity} "
                            f"units of "
                            f"{product.name} "
                            "are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -------------------------------------
            # Get database price
            # -------------------------------------

            unit_price = product.current_price

            item_total = (
                unit_price * quantity
            )

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
        # Calculate delivery
        # -----------------------------------------

        delivery_fee = get_delivery_fee(
            county
        )

        total = (
            subtotal +
            delivery_fee
        )

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
        # CASH ON DELIVERY
        # -----------------------------------------

        if payment_method == "cod":

            order.payment_status = "pending"

            order.save(
                update_fields=[
                    "payment_status",
                    "updated_at",
                ]
            )

            serializer = OrderSerializer(
                order
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # -----------------------------------------
        # CARD
        # -----------------------------------------

        if payment_method == "card":

            return Response(
                {
                    "error": (
                        "Card payments are "
                        "not available yet."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------
        # M-PESA PAYMENT
        # -----------------------------------------

        normalized_phone = phone

        # -----------------------------------------
        # Create payment record
        # -----------------------------------------

        payment = Payment.objects.create(

            order=order,

            phone_number=normalized_phone,

            amount=total,

            payment_method="mpesa",

        )

        # -----------------------------------------
        # Send STK Push
        # -----------------------------------------

        try:

            mpesa_response = (
                MpesaService.stk_push(

                    phone_number=normalized_phone,

                    amount=total,

                    account_reference=(
                        order.order_number
                    ),

                    transaction_description=(
                        "Anova Technologies "
                        "Order Payment"
                    ),
                )
            )

        except Exception as error:

            # -------------------------------------
            # STK Push failed
            # -------------------------------------

            payment.result_description = (
                str(error)
            )

            payment.save(
                update_fields=[
                    "result_description",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "error": (
                        "Unable to initiate "
                        "M-Pesa payment."
                    ),

                    "details": str(error),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # -----------------------------------------
        # Save Daraja transaction IDs
        # -----------------------------------------

        payment.merchant_request_id = (
            mpesa_response.get(
                "MerchantRequestID"
            )
        )

        payment.checkout_request_id = (
            mpesa_response.get(
                "CheckoutRequestID"
            )
        )

        payment.result_code = (
            mpesa_response.get(
                "ResponseCode"
            )
        )

        payment.result_description = (
            mpesa_response.get(
                "ResponseDescription"
            )
        )

        payment.save()

        # -----------------------------------------
        # Return order + payment information
        # -----------------------------------------

        serializer = OrderSerializer(
            order
        )

        return Response(
            {
                "order": serializer.data,

                "payment": {
                    "status": "pending",

                    "checkout_request_id":
                        payment.checkout_request_id,

                    "merchant_request_id":
                        payment.merchant_request_id,

                    "message": (
                        "M-Pesa payment prompt "
                        "sent to your phone."
                    ),
                },
            },
            status=status.HTTP_201_CREATED,
        )

class DeliveryFeeView(APIView):

    def get(self, request):
        county = request.query_params.get(
            "county",
            ""
        ).strip()

        if not county:
            return Response(
                {
                    "error": "County is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery_fee = get_delivery_fee(county)

        return Response(
            {
                "county": county,
                "delivery_fee": str(delivery_fee),
            },
            status=status.HTTP_200_OK,
        )