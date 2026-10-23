from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, filters

from products.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer, AdminOrderSerializer

from payments.models import Payment
from payments.mpesa import MpesaService
from payments.utils import normalize_kenyan_phone

from accounts.permissions import IsStaffOrAdmin


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
    """Create an order using trusted database prices, then initiate payment."""

    def post(self, request):
        customer = request.data.get("customer") or {}
        delivery = request.data.get("delivery") or {}
        items = request.data.get("items") or []
        payment_method = request.data.get("payment_method", "mpesa")

        # Validate payload structure before accessing fields.
        if not isinstance(customer, dict) or not isinstance(delivery, dict):
            return Response(
                {"error": "Invalid customer or delivery information."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(items, list) or not items:
            return Response(
                {"error": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate customer information.
        full_name = str(customer.get("full_name") or "").strip()
        email = str(customer.get("email") or "").strip()
        phone = str(customer.get("phone") or "").strip()

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

        normalized_phone = normalize_kenyan_phone(phone)
        if not normalized_phone:
            return Response(
                {"error": "Please enter a valid Kenyan phone number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate delivery information.
        county = str(delivery.get("county") or "").strip()
        town = str(delivery.get("town") or "").strip()
        address = str(delivery.get("address") or "").strip()

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

        if payment_method not in {"mpesa", "card", "cod"}:
            return Response(
                {"error": "Invalid payment method."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Card payments are not implemented; reject before creating an order.
        if payment_method == "card":
            return Response(
                {"error": "Card payments are not available yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Merge duplicate product IDs so stock validation cannot be bypassed
        # by submitting the same product in multiple cart rows.
        quantities_by_product = {}
        for item in items:
            if not isinstance(item, dict):
                return Response(
                    {"error": "Invalid cart item."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product_id = item.get("product_id")
            if not product_id:
                return Response(
                    {"error": "Product ID is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            raw_quantity = item.get("quantity")
            if isinstance(raw_quantity, bool):
                return Response(
                    {"error": "Invalid quantity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                quantity = int(raw_quantity)
            except (TypeError, ValueError, OverflowError):
                return Response(
                    {"error": "Invalid quantity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if quantity <= 0 or str(raw_quantity).strip() != str(quantity):
                return Response(
                    {"error": "Quantity must be a positive whole number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            key = str(product_id)
            quantities_by_product[key] = (
                quantities_by_product.get(key, 0) + quantity
            )

        # Build and save the order under a short database transaction. The
        # Safaricom network request happens after this transaction has committed.
        order_items = []
        subtotal = Decimal("0.00")

        with transaction.atomic():
            for product_id, quantity in quantities_by_product.items():
                try:
                    product = (
                        Product.objects.select_for_update()
                        .get(id=product_id, status="active")
                    )
                except (Product.DoesNotExist, ValueError, TypeError):
                    return Response(
                        {
                            "error": (
                                f"Product {product_id} does not exist "
                                "or is unavailable."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if product.stock_quantity < quantity:
                    return Response(
                        {
                            "error": (
                                f"Only {product.stock_quantity} units of "
                                f"{product.name} are available."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Use the pricing fields saved by the product creation form.
                # A sale price applies only when it is lower than the regular
                # price and its optional start/end dates make the sale active.
                # Never trust a price submitted by the browser.
                now = timezone.now()
                sale_is_valid = (
                    product.sale_price is not None
                    and product.sale_price > Decimal("0.00")
                    and product.sale_price < product.price
                    and (
                        product.sale_start_date is None
                        or product.sale_start_date <= now
                    )
                    and (
                        product.sale_end_date is None
                        or product.sale_end_date >= now
                    )
                )

                unit_price = Decimal(
                    str(product.sale_price if sale_is_valid else product.price)
                )
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

            delivery_fee = get_delivery_fee(county)
            total = subtotal + delivery_fee

            order = Order.objects.create(
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                full_name=full_name,
                email=email,
                phone=normalized_phone,
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

            if payment_method == "mpesa":
                payment = Payment.objects.create(
                    order=order,
                    phone_number=normalized_phone,
                    amount=total,
                    payment_method="mpesa",
                )

        # Cash on delivery does not require an M-Pesa request.
        if payment_method == "cod":
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED,
            )

        # Initiate M-Pesa after the order/payment records have committed.
        try:
            mpesa_response = MpesaService.stk_push(
                phone_number=normalized_phone,
                amount=total,
                account_reference=order.order_number,
                transaction_description="Anova Order Payment",
            )
        except Exception as error:
            payment.result_description = str(error)[:1000]
            payment.save(update_fields=["result_description", "updated_at"])
            return Response(
                {
                    "error": "Unable to initiate M-Pesa payment.",
                    "details": (
                        "Please retry or contact support if an order number "
                        "has already been created."
                    ),
                    "order_number": order.order_number,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payment.merchant_request_id = mpesa_response.get("MerchantRequestID")
        payment.checkout_request_id = mpesa_response.get("CheckoutRequestID")
        payment.result_code = mpesa_response.get("ResponseCode")
        payment.result_description = mpesa_response.get("ResponseDescription")
        payment.save(
            update_fields=[
                "merchant_request_id",
                "checkout_request_id",
                "result_code",
                "result_description",
                "updated_at",
            ]
        )

        return Response(
            {
                "order": OrderSerializer(order).data,
                "payment": {
                    "status": "pending",
                    "checkout_request_id": payment.checkout_request_id,
                    "merchant_request_id": payment.merchant_request_id,
                    "message": "M-Pesa payment prompt sent to your phone.",
                },
            },
            status=status.HTTP_201_CREATED,
        )


# =================================================
# ADMIN ORDERS
# =================================================

class AdminOrderListAPIView(
    generics.ListAPIView
):
    queryset = (
        Order.objects
        .all()
        .prefetch_related("items")
    )

    serializer_class = AdminOrderSerializer

    # Staff and Admin only
    permission_classes = [
        IsStaffOrAdmin
    ]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "order_number",
        "full_name",
        "email",
        "phone",
        "county",
        "town",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "total",
        "status",
        "payment_status",
    ]

    ordering = [
        "-created_at",
    ]


class AdminOrderDetailAPIView(
    generics.RetrieveUpdateAPIView
):
    queryset = (
        Order.objects
        .all()
        .prefetch_related("items")
    )

    serializer_class = AdminOrderSerializer

    # Staff and Admin only
    permission_classes = [
        IsStaffOrAdmin
    ]


class DeliveryFeeView(APIView):

    def get(self, request):

        county = request.query_params.get(
            "county",
            "",
        ).strip()

        if not county:
            return Response(
                {
                    "error": "County is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery_fee = get_delivery_fee(
            county
        )

        return Response(
            {
                "county": county,
                "delivery_fee": str(
                    delivery_fee
                ),
            },
            status=status.HTTP_200_OK,
        )