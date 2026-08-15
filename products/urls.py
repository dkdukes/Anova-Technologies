from django.urls import path
from . views import (
    CategoryListAPIView,
    BrandListAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
)


urlpatterns = [
    path("categories/",CategoryListAPIView.as_view(),name="category-list"),
    path("brands/",BrandListAPIView.as_view(),name="brand-list"),
    path("products/<slug:slug>/",ProductDetailAPIView.as_view(),name="product-detail"),
    path("products/",ProductListAPIView.as_view(),name="product-list"),
]