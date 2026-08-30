from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from . models import Payment

from .mpesa import MpesaService


class MpesaTestView(APIView):

    def get(self, request):

        try:
            token = MpesaService.get_access_token()

            return Response({
                "success": True,
                "message": "M-Pesa authentication successful.",
                "token_received": bool(token),
            })

        except Exception as error:

            return Response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=500,
            )


class MpesaStkTestView(APIView):

    def post(self, request):

        phone_number = request.data.get(
            "phone_number"
        )

        amount = request.data.get(
            "amount"
        )

        if not phone_number:
            return Response(
                {
                    "error": "Phone number is required."
                },
                status=400,
            )

        if not amount:
            return Response(
                {
                    "error": "Amount is required."
                },
                status=400,
            )

        try:

            response = MpesaService.stk_push(
                phone_number=phone_number,
                amount=Decimal(amount),
                account_reference="ANOVA-TEST",
                transaction_description=(
                    "Anova Technologies Test Payment"
                ),
            )

            return Response(response)

        except Exception as error:

            return Response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=500,
            )


class MpesaCallbackView(APIView):

    authentication_classes = []
    permission_classes = []

    @transaction.atomic
    def post(self, request):

        callback = request.data.get(
            "Body",
            {}
        )

        stk_callback = callback.get(
            "stkCallback",
            {}
        )

        merchant_request_id = (
            stk_callback.get(
                "MerchantRequestID"
            )
        )

        checkout_request_id = (
            stk_callback.get(
                "CheckoutRequestID"
            )
        )

        result_code = stk_callback.get(
            "ResultCode"
        )

        result_description = (
            stk_callback.get(
                "ResultDesc"
            )
        )

        # -----------------------------------------
        # Find payment
        # -----------------------------------------

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .select_related("order")
                .get(
                    checkout_request_id=(
                        checkout_request_id
                    )
                )
            )

        except Payment.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Payment not found."
                    )
                },
                status=404,
            )

        # -----------------------------------------
        # Save callback information
        # -----------------------------------------

        payment.merchant_request_id = (
            merchant_request_id
        )

        payment.result_code = (
            str(result_code)
            if result_code is not None
            else None
        )

        payment.result_description = (
            result_description
        )

        # -----------------------------------------
        # Successful payment
        # -----------------------------------------

        if result_code == 0:

            callback_metadata = (
                stk_callback.get(
                    "CallbackMetadata",
                    {}
                )
            )

            metadata_items = (
                callback_metadata.get(
                    "Item",
                    []
                )
            )

            metadata = {}

            for item in metadata_items:

                name = item.get("Name")

                value = item.get("Value")

                metadata[name] = value

            # -------------------------------------
            # M-Pesa receipt
            # -------------------------------------

            receipt_number = metadata.get(
                "MpesaReceiptNumber"
            )

            transaction_date = metadata.get(
                "TransactionDate"
            )

            payment.mpesa_receipt_number = (
                str(receipt_number)
                if receipt_number
                else None
            )

            payment.transaction_date = (
                str(transaction_date)
                if transaction_date
                else None
            )

            payment.save()

            # -------------------------------------
            # Mark payment as paid
            # -------------------------------------

            payment.order.payment_status = (
                "paid"
            )

            payment.order.save(
                update_fields=[
                    "payment_status",
                    "updated_at",
                ]
            )

            # -------------------------------------
            # Reduce stock
            # -------------------------------------

            for order_item in (
                payment.order.items.select_for_update()
            ):

                product = order_item.product

                product.stock_quantity -= (
                    order_item.quantity
                )

                product.save(
                    update_fields=[
                        "stock_quantity"
                    ]
                )

            return Response(
                {
                    "ResultCode": 0,
                    "ResultDesc": (
                        "Payment processed successfully."
                    ),
                },
                status=200,
            )

        # -----------------------------------------
        # Failed / cancelled payment
        # -----------------------------------------

        payment.save()

        payment.order.payment_status = (
            "failed"
        )

        payment.order.save(
            update_fields=[
                "payment_status",
                "updated_at",
            ]
        )

        return Response(
            {
                "ResultCode": 0,
                "ResultDesc": (
                    "Callback received."
                ),
            },
            status=200,
        )