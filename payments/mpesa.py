import base64
from datetime import datetime

import requests

from django.conf import settings


class MpesaService:

    BASE_URL = (
        "https://sandbox.safaricom.co.ke"
    )

    @classmethod
    def get_access_token(cls):
        """
        Get OAuth access token from
        Safaricom Daraja.
        """

        url = (
            f"{cls.BASE_URL}"
            "/oauth/v1/generate"
            "?grant_type=client_credentials"
        )

        credentials = (
            f"{settings.MPESA_CONSUMER_KEY}:"
            f"{settings.MPESA_CONSUMER_SECRET}"
        )

        encoded_credentials = base64.b64encode(
            credentials.encode()
        ).decode()

        headers = {
            "Authorization": (
                f"Basic {encoded_credentials}"
            ),
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()["access_token"]