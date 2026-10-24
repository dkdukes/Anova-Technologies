
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from orders.models import OrderItem
from .models import Review
from .serializers import ReviewSerializer


def customer_can_review(user, product):
    """
    A customer can review a product only if it appears
    in one of their delivered orders.
    """
    return OrderItem.objects.filter(
        order__user=user,
        order__status="delivered",
        product=product,
    ).exists()


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(
            product__slug=self.kwargs["slug"],
            is_approved=True,
        ).select_related("user", "product")


class ProductReviewCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        product = get_object_or_404(
            Product,
            slug=slug,
        )

        # Verify that the customer purchased and received the product.
        if not customer_can_review(request.user, product):
            return Response(
                {
                    "detail": (
                        "You can review this product only after "
                        "purchasing and receiving it."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                review = Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=serializer.validated_data["rating"],
                    title=serializer.validated_data.get("title", ""),
                    comment=serializer.validated_data["comment"],
                    is_approved=False,
                )

        except IntegrityError:
            raise ValidationError({
                "detail": (
                    "You have already reviewed this product. "
                    "Update your existing review instead."
                )
            })

        return Response(
            {
                "message": (
                    "Your review has been submitted for approval."
                ),
                "review": ReviewSerializer(review).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ProductReviewEligibilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        product = get_object_or_404(
            Product,
            slug=slug,
        )

        can_review = customer_can_review(
            request.user,
            product,
        )

        has_review = Review.objects.filter(
            product=product,
            user=request.user,
        ).exists()

        return Response({
            "can_review": can_review,
            "has_review": has_review,
        })
