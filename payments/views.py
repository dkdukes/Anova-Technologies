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

            return Response({
                "success": False,
                "error": str(error),
            }, status=500)