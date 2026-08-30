from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView

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