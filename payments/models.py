from django.db import models


class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("mpesa", "M-Pesa"),
        ("card", "Card"),
        ("cod", "Cash on Delivery"),
    ]

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment",
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="mpesa",
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    transaction_date = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    result_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    result_description = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.order.order_number} - "
            f"{self.payment_method}"
        )