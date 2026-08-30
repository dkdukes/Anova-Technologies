import base64
from datetime import datetime

import requests

from django.conf import settings


class MpesaService:

    BASE_URL = "https://sandbox.safaricom.co.ke"

    @classmethod
    def get_access_token(cls):
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
            "Authorization": f"Basic {encoded_credentials}",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()["access_token"]

    @classmethod
    def generate_password(cls):
        """
        Generate the password required by
        the M-Pesa STK Push API.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        raw_password = (
            f"{settings.MPESA_SHORTCODE}"
            f"{settings.MPESA_PASSKEY}"
            f"{timestamp}"
        )

        password = base64.b64encode(
            raw_password.encode()
        ).decode()

        return password, timestamp

    @classmethod
    def stk_push(
        cls,
        phone_number,
        amount,
        account_reference,
        transaction_description,
    ):
        """
        Send an M-Pesa STK Push request.
        """

        access_token = cls.get_access_token()

        password, timestamp = (
            cls.generate_password()
        )

        url = (
            f"{cls.BASE_URL}"
            "/mpesa/stkpush/v1/processrequest"
        )

        payload = {
            "BusinessShortCode":
                settings.MPESA_SHORTCODE,

            "Password":
                password,

            "Timestamp":
                timestamp,

            "TransactionType":
                "CustomerPayBillOnline",

            "Amount":
                int(amount),

            "PartyA":
                phone_number,

            "PartyB":
                settings.MPESA_SHORTCODE,

            "PhoneNumber":
                phone_number,

            "CallBackURL":
                settings.MPESA_CALLBACK_URL,

            "AccountReference":
                account_reference,

            "TransactionDesc":
                transaction_description,
        }

        headers = {
            "Authorization":
                f"Bearer {access_token}",

            "Content-Type":
                "application/json",
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if not response.ok:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {
                    "raw_response": response.text
                }

            raise Exception(
                f"Daraja STK Push error "
                f"(HTTP {response.status_code}): "
                f"{error_data}"
            )

        return response.json()