from rest_framework import (
    generics,
    filters,
)

from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    SpecificationTemplate,
)

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    ProductSpecificationSerializer,
    SpecificationTemplateSerializer,
)


import cloudinary.uploader

from rest_framework import (
    generics,
    filters,
    status,
)

from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    SpecificationTemplate,
    StoreSettings
)

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    ProductSpecificationSerializer,
    SpecificationTemplateSerializer,
    AdminCategorySerializer,
    AdminBrandSerializer,
    AdminBrandDetailSerializer,
    AdminBrandProductSerializer,
    AdminProductSerializer,
    StoreSettingsSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models

from django.db.models import Sum

from .models import Product


class BrandLogoUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        image = request.FILES.get("logo")
        brand_id = request.data.get("brand_id")

        if not image:
            return Response(
                {"error": "Logo image is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not brand_id:
            return Response(
                {"error": "brand_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            brand = Brand.objects.get(id=brand_id)
        except Brand.DoesNotExist:
            return Response(
                {"error": "Brand not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 5 MB limit
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {"error": "Logo must be less than 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = cloudinary.uploader.upload(
                image,
                folder="anova-technologies/brands",
                resource_type="image",
            )

            cloudinary_url = result.get("secure_url")

            if not cloudinary_url:
                return Response(
                    {"error": "Cloudinary did not return an image URL."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            brand.logo = cloudinary_url
            brand.save(update_fields=["logo"])

            return Response(
                {
                    "message": "Brand logo uploaded successfully.",
                    "brand": {
                        "id": brand.id,
                        "name": brand.name,
                        "slug": brand.slug,
                        "logo": brand.logo,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "error": "Brand logo upload failed.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class AdminProductImageUploadAPIView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, product_id):

        # -------------------------
        # Get product
        # -------------------------
        try:
            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:
            return Response(
                {
                    "error": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -------------------------
        # Get image
        # -------------------------
        image = request.FILES.get("image")

        if not image:
            return Response(
                {
                    "error": "No image was provided."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------
        # Validate file size
        # -------------------------
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {
                    "error": "Image size cannot exceed 5MB."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------
        # Other fields
        # -------------------------
        alt_text = request.data.get(
            "alt_text",
            product.name
        )

        is_primary = (
            str(
                request.data.get(
                    "is_primary",
                    "false"
                )
            ).lower()
            == "true"
        )

        try:
            sort_order = int(
                request.data.get(
                    "sort_order",
                    0
                )
            )

        except (TypeError, ValueError):
            sort_order = 0

        # -------------------------
        # Upload to Cloudinary
        # -------------------------
        try:

            result = cloudinary.uploader.upload(
                image,
                folder="anova-technologies/products",
                resource_type="image",
            )

            cloudinary_url = result.get(
                "secure_url"
            )

            if not cloudinary_url:
                return Response(
                    {
                        "error": (
                            "Cloudinary did not return "
                            "an image URL."
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # -------------------------
            # Handle primary image
            # -------------------------
            if is_primary:

                ProductImage.objects.filter(
                    product=product,
                    is_primary=True
                ).update(
                    is_primary=False
                )

            # -------------------------
            # Create ProductImage
            # -------------------------
            product_image = ProductImage.objects.create(
                product=product,
                image_url=cloudinary_url,
                alt_text=alt_text,
                is_primary=is_primary,
                sort_order=sort_order,
            )

            # -------------------------
            # Serialize response
            # -------------------------
            serializer = ProductImageSerializer(
                product_image
            )

            return Response(
                {
                    "message": (
                        "Image uploaded successfully."
                    ),
                    "image": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:

            return Response(
                {
                    "error": "Image upload failed.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class AdminBrandListCreateAPIView(generics.ListCreateAPIView):
    queryset = Brand.objects.all().prefetch_related("products")
    serializer_class = AdminBrandSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
    ]

    ordering_fields = [
        "name",
        "is_active",
    ]

    ordering = [
        "name",
    ]


class AdminBrandDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all().prefetch_related("products")
    serializer_class = AdminBrandDetailSerializer




class CategoryImageUploadAPIView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, *args, **kwargs):

        image = request.FILES.get("image")
        category_id = request.data.get("category_id")

        # Validate image
        if not image:
            return Response(
                {
                    "error": "No image was provided."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate category
        if not category_id:
            return Response(
                {
                    "error": "category_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find category
        try:
            category = Category.objects.get(
                id=category_id
            )

        except Category.DoesNotExist:
            return Response(
                {
                    "error": "Category not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate file size
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {
                    "error": "Image must be less than 5MB."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image,
                folder="anova-technologies/categories",
                resource_type="image",
            )

            cloudinary_url = result.get(
                "secure_url"
            )

            if not cloudinary_url:
                return Response(
                    {
                        "error": "Cloudinary did not return an image URL."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Save URL
            category.image = cloudinary_url

            category.save(
                update_fields=["image"]
            )

            return Response(
                {
                    "message": "Category image uploaded successfully.",
                    "category": {
                        "id": category.id,
                        "name": category.name,
                        "slug": category.slug,
                        "image": category.image,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:

            return Response(
                {
                    "error": "Category image upload failed.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class AdminCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = (
        Category.objects
        .all()
        .prefetch_related("products")
        .order_by("-created_at")
    )

    serializer_class = AdminCategorySerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "is_active",
    ]

    ordering = ["-created_at"]


class AdminCategoryDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = (
        Category.objects
        .all()
        .prefetch_related("products")
    )

    serializer_class = AdminCategorySerializer



class AdminDashboardStatsAPIView(APIView):

    def get(self, request):
        total_products = Product.objects.count()

        active_products = Product.objects.filter(
            status="active"
        ).count()

        draft_products = Product.objects.filter(
            status="draft"
        ).count()

        low_stock_products = Product.objects.filter(
            stock_quantity__lte=models.F("low_stock_threshold")
        ).count()

        total_stock = Product.objects.aggregate(
            total=Sum("stock_quantity")
        )["total"] or 0

        return Response({
            "total_products": total_products,
            "active_products": active_products,
            "draft_products": draft_products,
            "low_stock_products": low_stock_products,
            "total_stock": total_stock,
        })


class AdminProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all().select_related(
        "category",
        "brand",
    ).prefetch_related(
        "images",
        "specifications",
    )

    serializer_class = AdminProductSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
        "sku",
        "category__name",
        "brand__name",
    ]

    ordering_fields = [
        "name",
        "price",
        "sale_price",
        "stock_quantity",
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = [
        "-created_at",
    ]


class AdminProductDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Product.objects.all().select_related(
        "category",
        "brand",
    ).prefetch_related(
        "images",
        "specifications",
    )

    serializer_class = AdminProductSerializer

class CategoryListAPIView(
    generics.ListAPIView
):

    queryset = Category.objects.filter(
        is_active=True
    )

    serializer_class = CategorySerializer

    filter_backends = [
        filters.SearchFilter,
    ]

    search_fields = [
        "name",
    ]


class AdminProductImageListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]

        return ProductImage.objects.filter(
            product_id=product_id
        ).order_by(
            "sort_order",
            "-created_at"
        )

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]

        serializer.save(
            product_id=product_id
        )


class AdminProductImageDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]

        return ProductImage.objects.filter(
            product_id=product_id
        )


class AdminProductImageReplaceAPIView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def patch(self, request, product_id, pk):

        try:
            product_image = ProductImage.objects.get(
                id=pk,
                product_id=product_id,
            )
        except ProductImage.DoesNotExist:
            return Response(
                {"error": "Product image not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        image = request.FILES.get("image")

        if not image:
            return Response(
                {"error": "No image was provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5MB limit
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {"error": "Image size cannot exceed 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = cloudinary.uploader.upload(
                image,
                folder="anova-technologies/products",
                resource_type="image",
            )

            cloudinary_url = result.get("secure_url")

            if not cloudinary_url:
                return Response(
                    {
                        "error": (
                            "Cloudinary did not return "
                            "an image URL."
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Replace the existing image URL
            product_image.image_url = cloudinary_url

            # Optionally update alt text
            alt_text = request.data.get("alt_text")

            if alt_text is not None:
                product_image.alt_text = alt_text

            product_image.save()

            serializer = ProductImageSerializer(
                product_image
            )

            return Response(
                {
                    "message": "Image replaced successfully.",
                    "image": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "error": "Image replacement failed.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )    

class BrandListAPIView(
    generics.ListAPIView
):

    queryset = Brand.objects.filter(
        is_active=True
    )

    serializer_class = BrandSerializer

    filter_backends = [
        filters.SearchFilter,
    ]

    search_fields = [
        "name",
    ]


class SpecificationTemplateListAPIView(
    generics.ListAPIView
):

    serializer_class = SpecificationTemplateSerializer

    def get_queryset(self):

        category_id = self.request.query_params.get(
            "category"
        )

        if category_id:

            return SpecificationTemplate.objects.filter(
                category_id=category_id
            )

        return SpecificationTemplate.objects.none()


class ProductListAPIView(
    generics.ListCreateAPIView
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


class ProductImageCreateAPIView(
    generics.CreateAPIView
):

    queryset = ProductImage.objects.all()

    serializer_class = ProductImageSerializer


class ProductSpecificationCreateAPIView(
    generics.CreateAPIView
):

    queryset = ProductSpecification.objects.all()

    serializer_class = ProductSpecificationSerializer



class AdminStoreSettingsAPIView(APIView):

    def get(self, request):
        settings = StoreSettings.objects.first()

        if not settings:
            settings = StoreSettings.objects.create(
                store_name="Anova Technologies",
                country="Kenya",
            )

        serializer = StoreSettingsSerializer(settings)

        return Response(serializer.data)

    def patch(self, request):
        settings = StoreSettings.objects.first()

        if not settings:
            settings = StoreSettings.objects.create(
                store_name="Anova Technologies",
                country="Kenya",
            )

        serializer = StoreSettingsSerializer(
            settings,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )