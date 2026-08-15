from django.shortcuts import render
from rest_framework import generics, filters
from . models import (
    Brand,
    Category,
    Product,
)
from . serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
)

# Create your views here.
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active = True)
    serializer_class = CategorySerializer
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = [
        "name",
    ]

class BrandListAPIView(generics.ListAPIView):
    queryset = Brand.objects.filter(is_active = True)
    serializer_class = BrandSerializer
    filter_backends = [
        filters.SearchFilter,
    ]
    filter_fields = [
        "name",
    ]


class ProductListAPIView(generics.ListAPIView):

    queryset = (
        Product.objects
        .filter(status="active")
        .select_related(
            "category",
            "brand",
        )
        .prefetch_related(
            "images",
            "specifications",
        )
    )

    serializer_class = ProductSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
        "sku",
        "short_description",
        "description",
        "brand__name",
        "category__name",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
        "stock_quantity",
    ]

    ordering = [
        "-created_at",
    ]


class ProductDetailAPIView(
    generics.RetrieveAPIView
):

    queryset = (
        Product.objects
        .filter(status="active")
        .select_related(
            "category",
            "brand",
        )
        .prefetch_related(
            "images",
            "specifications",
        )
    )

    serializer_class = ProductSerializer

    lookup_field = "slug"