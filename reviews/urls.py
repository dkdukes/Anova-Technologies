
from django.urls import path

from .views import (
    ProductReviewListView,
    ProductReviewCreateView,
    ProductReviewEligibilityView,
)

urlpatterns = [
    path(
        "products/<slug:slug>/reviews/",
        ProductReviewListView.as_view(),
        name="product-review-list",
    ),
    path(
        "products/<slug:slug>/reviews/create/",
        ProductReviewCreateView.as_view(),
        name="product-review-create",
    ),
    path(
        "products/<slug:slug>/reviews/eligibility/",
        ProductReviewEligibilityView.as_view(),
        name="product-review-eligibility",
    ),
]
