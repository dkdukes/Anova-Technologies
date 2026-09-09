from django.db import models
from django.db.models import Sum

from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

import cloudinary.uploader

from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    SpecificationTemplate,
    StoreSettings,
    Course,
    Usage,
)

from accounts.permissions import IsStaffOrAdmin

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    ProductSpecificationSerializer,
    SpecificationTemplateSerializer,
    UsageSerializer,
    CourseSerializer,
    AdminCategorySerializer,
    AdminBrandSerializer,
    AdminBrandDetailSerializer,
    AdminBrandProductSerializer,
    AdminProductSerializer,
    StoreSettingsSerializer,
    LaptopRecommendationSerializer
)


# ============================================================
# BRAND LOGO UPLOAD
# ============================================================

class BrandLogoUploadAPIView(APIView):
    permission_classes = [IsStaffOrAdmin]

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
                    {
                        "error": (
                            "Cloudinary did not return an image URL."
                        )
                    },
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


# ============================================================
# ADMIN PRODUCT IMAGE UPLOAD
# ============================================================

class AdminProductImageUploadAPIView(APIView):
    permission_classes = [IsStaffOrAdmin]

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):

        # Get product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get image
        image = request.FILES.get("image")

        if not image:
            return Response(
                {"error": "No image was provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {"error": "Image size cannot exceed 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Other fields
        alt_text = request.data.get(
            "alt_text",
            product.name,
        )

        is_primary = (
            str(
                request.data.get(
                    "is_primary",
                    "false",
                )
            ).lower()
            == "true"
        )

        try:
            sort_order = int(
                request.data.get(
                    "sort_order",
                    0,
                )
            )
        except (TypeError, ValueError):
            sort_order = 0

        # Upload to Cloudinary
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

            # Handle primary image
            if is_primary:
                ProductImage.objects.filter(
                    product=product,
                    is_primary=True,
                ).update(
                    is_primary=False
                )

            # Create ProductImage
            product_image = ProductImage.objects.create(
                product=product,
                image_url=cloudinary_url,
                alt_text=alt_text,
                is_primary=is_primary,
                sort_order=sort_order,
            )

            # Serialize response
            serializer = ProductImageSerializer(
                product_image
            )

            return Response(
                {
                    "message": "Image uploaded successfully.",
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


# ============================================================
# ADMIN BRAND
# ============================================================

class AdminBrandListCreateAPIView(
    generics.ListCreateAPIView
):
    permission_classes = [IsStaffOrAdmin]

    queryset = (
        Brand.objects
        .all()
        .prefetch_related("products")
    )

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


class AdminBrandDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsStaffOrAdmin]

    queryset = (
        Brand.objects
        .all()
        .prefetch_related("products")
    )

    serializer_class = AdminBrandDetailSerializer


# ============================================================
# CATEGORY IMAGE UPLOAD
# ============================================================

class CategoryImageUploadAPIView(APIView):
    permission_classes = [IsStaffOrAdmin]

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):

        image = request.FILES.get("image")
        category_id = request.data.get("category_id")

        # Validate image
        if not image:
            return Response(
                {"error": "No image was provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate category
        if not category_id:
            return Response(
                {"error": "category_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find category
        try:
            category = Category.objects.get(
                id=category_id
            )
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate file size
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {"error": "Image must be less than 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image,
                folder="anova-technologies/categories",
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

            # Save URL
            category.image = cloudinary_url

            category.save(
                update_fields=["image"]
            )

            return Response(
                {
                    "message": (
                        "Category image uploaded "
                        "successfully."
                    ),
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


# ============================================================
# ADMIN CATEGORY
# ============================================================

class AdminCategoryListCreateAPIView(
    generics.ListCreateAPIView
):
    permission_classes = [IsStaffOrAdmin]

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

    ordering = [
        "-created_at"
    ]


class AdminCategoryDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsStaffOrAdmin]

    queryset = (
        Category.objects
        .all()
        .prefetch_related("products")
    )

    serializer_class = AdminCategorySerializer


# ============================================================
# ADMIN DASHBOARD STATS
# ============================================================

class AdminDashboardStatsAPIView(APIView):
    permission_classes = [IsStaffOrAdmin]


    def get(self, request):

        total_products = Product.objects.count()

        active_products = Product.objects.filter(
            status="active"
        ).count()

        draft_products = Product.objects.filter(
            status="draft"
        ).count()

        low_stock_products = Product.objects.filter(
            stock_quantity__lte=models.F(
                "low_stock_threshold"
            )
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


# ============================================================
# ADMIN PRODUCT LIST
# ============================================================

class AdminProductListAPIView(
    generics.ListAPIView
):
    permission_classes = [IsStaffOrAdmin]

    queryset = (
        Product.objects
        .all()
        .select_related(
            "category",
            "brand",
        )
        .prefetch_related(
            "images",
            "specifications",
            "usage",
            "courses",
        )
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


# ============================================================
# ADMIN PRODUCT DETAIL
# ============================================================

class AdminProductDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsStaffOrAdmin]

    queryset = (
        Product.objects
        .all()
        .select_related(
            "category",
            "brand",
        )
        .prefetch_related(
            "images",
            "specifications",
            "usage",
            "courses",
        )
    )

    serializer_class = AdminProductSerializer


# ============================================================
# CATEGORY LIST
# ============================================================

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


# ============================================================
# USAGE LIST
# ============================================================

class UsageListAPIView(
    generics.ListAPIView
):
    queryset = (
        Usage.objects
        .filter(is_active=True)
        .order_by("name")
    )

    serializer_class = UsageSerializer


# ============================================================
# COURSE LIST
# ============================================================

class CourseListAPIView(
    generics.ListAPIView
):
    queryset = (
        Course.objects
        .filter(is_active=True)
        .select_related("usage")
        .order_by("name")
    )

    serializer_class = CourseSerializer


# ============================================================
# ADMIN PRODUCT IMAGE LIST / CREATE
# ============================================================

class AdminProductImageListCreateAPIView(
    generics.ListCreateAPIView
):
    permission_classes = [IsStaffOrAdmin]

    serializer_class = ProductImageSerializer

    def get_queryset(self):

        product_id = self.kwargs["product_id"]

        return (
            ProductImage.objects
            .filter(product_id=product_id)
            .order_by(
                "sort_order",
                "-created_at",
            )
        )

    def perform_create(self, serializer):

        product_id = self.kwargs["product_id"]

        serializer.save(
            product_id=product_id
        )


# ============================================================
# ADMIN PRODUCT IMAGE DETAIL
# ============================================================

class AdminProductImageDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsStaffOrAdmin]

    serializer_class = ProductImageSerializer

    def get_queryset(self):

        product_id = self.kwargs["product_id"]

        return ProductImage.objects.filter(
            product_id=product_id
        )


# ============================================================
# ADMIN PRODUCT IMAGE REPLACE
# ============================================================

class AdminProductImageReplaceAPIView(APIView):
    permission_classes = [IsStaffOrAdmin]

    parser_classes = [MultiPartParser, FormParser]

    def patch(
        self,
        request,
        product_id,
        pk,
    ):

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

        # 5 MB limit
        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            return Response(
                {
                    "error": (
                        "Image size cannot exceed 5MB."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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

            # Replace existing image URL
            product_image.image_url = cloudinary_url

            # Optionally update alt text
            alt_text = request.data.get(
                "alt_text"
            )

            if alt_text is not None:
                product_image.alt_text = alt_text

            product_image.save()

            serializer = ProductImageSerializer(
                product_image
            )

            return Response(
                {
                    "message": (
                        "Image replaced successfully."
                    ),
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


# ============================================================
# BRAND LIST
# ============================================================

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


# ============================================================
# SPECIFICATION TEMPLATE LIST
# ============================================================

class SpecificationTemplateListAPIView(
    generics.ListAPIView
):
    serializer_class = SpecificationTemplateSerializer

    def get_queryset(self):

        category_id = (
            self.request.query_params.get(
                "category"
            )
        )

        if category_id:

            return SpecificationTemplate.objects.filter(
                category_id=category_id
            )

        return SpecificationTemplate.objects.none()


# ============================================================
# PRODUCT LIST / CREATE
# ============================================================

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
            "usage",
            "courses",
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

    def get_queryset(self):

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
                "usage",
                "courses",
            )
        )

        # ========================================================
        # SEARCH
        # ========================================================

        search = self.request.query_params.get(
            "search"
        )

        if search:

            queryset = queryset.filter(
                models.Q(
                    name__icontains=search
                )
                | models.Q(
                    sku__icontains=search
                )
                | models.Q(
                    short_description__icontains=search
                )
                | models.Q(
                    description__icontains=search
                )
                | models.Q(
                    brand__name__icontains=search
                )
                | models.Q(
                    category__name__icontains=search
                )
            )

        # ========================================================
        # CATEGORY FILTER
        # ========================================================

        category = self.request.query_params.get(
            "category"
        )

        if category:

            # Accessories should match:
            # Computer Accessories
            # Phone Accessories
            # Laptop Accessories
            # etc.
            if category.lower() == "accessories":

                queryset = queryset.filter(
                    category__name__icontains="accessories"
                )

            else:

                queryset = queryset.filter(
                    category__slug__iexact=category
                )

        # ========================================================
        # BRAND FILTER
        # ========================================================

        brand = self.request.query_params.get(
            "brand"
        )

        if brand:

            queryset = queryset.filter(
                brand__slug__iexact=brand
            )

        # ========================================================
        # USAGE FILTER
        # ========================================================

        usage = self.request.query_params.get(
            "usage"
        )

        if usage:

            queryset = queryset.filter(
                usage__slug__iexact=usage
            ).distinct()

        # ========================================================
        # COURSE FILTER
        # ========================================================

        course = self.request.query_params.get(
            "course"
        )

        if course:

            queryset = queryset.filter(
                courses__slug__iexact=course
            ).distinct()

        # ========================================================
        # FLASH SALE
        # ========================================================

        sale = self.request.query_params.get(
            "sale"
        )

        if sale and sale.lower() == "true":

            queryset = queryset.filter(
                sale_price__isnull=False,
                sale_price__lt=models.F("price"),
                stock_quantity__gt=0,
            )

        return queryset


# ============================================================
# LAPTOP RECOMMENDATION ENGINE
# ============================================================

def normalize_text(value):
    """
    Convert specification text into a normalized lowercase string.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def get_product_specifications(product):
    """
    Convert ProductSpecification records into a dictionary.

    Example:

    {
        "processor": "Intel Core i5",
        "ram": "16GB",
        "storage": "512GB SSD",
        "graphics": "Intel Iris Xe"
    }
    """

    specs = {}

    for specification in product.specifications.all():

        name = normalize_text(
            specification.name
        )

        value = normalize_text(
            specification.value
        )

        if name:
            specs[name] = value

    return specs


def find_specification(specs, keywords):
    """
    Find a specification using multiple possible names.

    For example:
    RAM may be stored as:
        RAM
        Memory
        System Memory
    """

    for name, value in specs.items():

        for keyword in keywords:

            if keyword in name:
                return value

    return ""


def extract_number(value):
    """
    Extract the first numeric value from a string.

    Examples:

        '16GB'       -> 16
        '512 GB SSD' -> 512
        'Core i5'    -> 5
    """

    import re

    if not value:
        return None

    match = re.search(
        r"\d+(?:\.\d+)?",
        str(value)
    )

    if not match:
        return None

    try:
        return float(match.group())

    except ValueError:
        return None


def get_ram_gb(specs):
    """
    Extract RAM amount in GB.
    """

    value = find_specification(
        specs,
        [
            "ram",
            "memory",
        ]
    )

    number = extract_number(value)

    if number is None:
        return 0

    return int(number)


def get_storage_gb(specs):
    """
    Extract storage capacity.

    Handles:
        256GB
        512GB
        1TB
        2TB
    """

    value = find_specification(
        specs,
        [
            "storage",
            "hard drive",
            "hard disk",
            "disk",
            "ssd",
            "hdd",
        ]
    )

    if not value:
        return 0

    number = extract_number(value)

    if number is None:
        return 0

    value_lower = value.lower()

    if "tb" in value_lower:
        return int(number * 1024)

    return int(number)


def get_cpu_score(specs):
    """
    Estimate CPU performance.

    This deliberately supports common Intel and AMD naming.
    """

    cpu = find_specification(
        specs,
        [
            "processor",
            "cpu",
            "chipset",
        ]
    )

    cpu = cpu.lower()

    if not cpu:
        return 0

    score = 0

    # --------------------------------------------------------
    # Intel
    # --------------------------------------------------------

    if "core i9" in cpu:
        score = 40

    elif "core i7" in cpu:
        score = 35

    elif "core i5" in cpu:
        score = 30

    elif "core i3" in cpu:
        score = 20

    # --------------------------------------------------------
    # Intel Core Ultra
    # --------------------------------------------------------

    elif "ultra 9" in cpu:
        score = 40

    elif "ultra 7" in cpu:
        score = 35

    elif "ultra 5" in cpu:
        score = 30

    # --------------------------------------------------------
    # AMD Ryzen
    # --------------------------------------------------------

    elif "ryzen 9" in cpu:
        score = 40

    elif "ryzen 7" in cpu:
        score = 35

    elif "ryzen 5" in cpu:
        score = 30

    elif "ryzen 3" in cpu:
        score = 20

    # --------------------------------------------------------
    # Apple
    # --------------------------------------------------------

    elif "m4" in cpu:
        score = 40

    elif "m3" in cpu:
        score = 38

    elif "m2" in cpu:
        score = 35

    elif "m1" in cpu:
        score = 32

    return score


def get_gpu_score(specs):
    """
    Estimate graphics capability.
    """

    gpu = find_specification(
        specs,
        [
            "graphics",
            "gpu",
            "video",
            "graphics card",
        ]
    )

    gpu = gpu.lower()

    if not gpu:
        return 0

    # Dedicated GPUs
    if (
        "rtx 4090" in gpu
        or "rtx 4080" in gpu
        or "rtx 4070" in gpu
    ):
        return 30

    if (
        "rtx 4060" in gpu
        or "rtx 4050" in gpu
    ):
        return 27

    if (
        "rtx 3060" in gpu
        or "rtx 3050" in gpu
    ):
        return 24

    if "gtx 1660" in gpu:
        return 22

    if "gtx 1650" in gpu:
        return 20

    if "radeon rx" in gpu:
        return 24

    # Integrated graphics
    if "iris xe" in gpu:
        return 12

    if "radeon graphics" in gpu:
        return 10

    if "uhd graphics" in gpu:
        return 8

    if "vega" in gpu:
        return 8

    return 5


def get_usage_match_score(product, usage_slug):
    """
    Score how closely the product is associated with
    the selected usage.
    """

    if not usage_slug:
        return 0

    usage_slug = usage_slug.lower()

    for usage in product.usage.all():

        if (
            usage.slug.lower() == usage_slug
            or usage.name.lower() == usage_slug
        ):
            return 20

    return 0


def get_course_match_score(product, course_slug):
    """
    Score how closely the laptop is associated with
    the selected course.
    """

    if not course_slug:
        return 0

    course_slug = course_slug.lower()

    for course in product.courses.all():

        if (
            course.slug.lower() == course_slug
            or course.name.lower() == course_slug
        ):
            return 15

    return 0


def get_usage_requirements(
    usage_slug=None,
    course_slug=None,
):
    """
    Determine the technical requirements based on usage.

    These are baseline requirements, not hard filters.
    """

    usage = (
        usage_slug or ""
    ).lower()

    course = (
        course_slug or ""
    ).lower()

    requirements = {
        "min_ram": 8,
        "min_storage": 256,
        "min_cpu_score": 20,
        "gpu_required": False,
    }

    # --------------------------------------------------------
    # Student
    # --------------------------------------------------------

    if "student" in usage:

        requirements.update({
            "min_ram": 8,
            "min_storage": 256,
            "min_cpu_score": 20,
        })

    # --------------------------------------------------------
    # Programming
    # --------------------------------------------------------

    elif (
        "program" in usage
        or "developer" in usage
        or "coding" in usage
    ):

        requirements.update({
            "min_ram": 16,
            "min_storage": 512,
            "min_cpu_score": 30,
        })

    # --------------------------------------------------------
    # Gaming
    # --------------------------------------------------------

    elif "gaming" in usage:

        requirements.update({
            "min_ram": 16,
            "min_storage": 512,
            "min_cpu_score": 30,
            "gpu_required": True,
        })

    # --------------------------------------------------------
    # Design / Creative
    # --------------------------------------------------------

    elif (
        "design" in usage
        or "creative" in usage
        or "graphic" in usage
    ):

        requirements.update({
            "min_ram": 16,
            "min_storage": 512,
            "min_cpu_score": 30,
            "gpu_required": True,
        })

    # --------------------------------------------------------
    # Business
    # --------------------------------------------------------

    elif "business" in usage:

        requirements.update({
            "min_ram": 8,
            "min_storage": 256,
            "min_cpu_score": 20,
        })

    # --------------------------------------------------------
    # Professional
    # --------------------------------------------------------

    elif "professional" in usage:

        requirements.update({
            "min_ram": 16,
            "min_storage": 512,
            "min_cpu_score": 30,
        })

    # --------------------------------------------------------
    # Course-specific improvements
    # --------------------------------------------------------

    if any(
        keyword in course
        for keyword in [
            "computer-science",
            "computer science",
            "software-engineering",
            "software engineering",
            "information-technology",
            "information technology",
            "cyber-security",
            "cyber security",
        ]
    ):

        requirements.update({
            "min_ram": max(
                requirements["min_ram"],
                16,
            ),
            "min_storage": max(
                requirements["min_storage"],
                512,
            ),
            "min_cpu_score": max(
                requirements["min_cpu_score"],
                30,
            ),
        })

    if any(
        keyword in course
        for keyword in [
            "data-science",
            "data science",
            "machine-learning",
            "machine learning",
            "artificial-intelligence",
            "artificial intelligence",
        ]
    ):

        requirements.update({
            "min_ram": 16,
            "min_storage": 512,
            "min_cpu_score": 35,
        })

    return requirements


def calculate_laptop_score(
    product,
    usage_slug=None,
    course_slug=None,
):
    """
    Calculate a suitability score for a laptop.

    Maximum score: 100
    """

    specs = get_product_specifications(
        product
    )

    requirements = get_usage_requirements(
        usage_slug,
        course_slug,
    )

    score = 0

    reasons = []

    # ========================================================
    # USAGE MATCH
    # ========================================================

    usage_score = get_usage_match_score(
        product,
        usage_slug,
    )

    if usage_score:

        score += usage_score

        reasons.append(
            "Matches your selected usage"
        )

    # ========================================================
    # COURSE MATCH
    # ========================================================

    course_score = get_course_match_score(
        product,
        course_slug,
    )

    if course_score:

        score += course_score

        reasons.append(
            "Matches your selected course"
        )

    # ========================================================
    # RAM
    # ========================================================

    ram = get_ram_gb(specs)

    if ram >= requirements["min_ram"]:

        score += 15

        reasons.append(
            f"{ram}GB RAM meets the recommended requirement"
        )

    elif ram >= 8:

        score += 8

        reasons.append(
            f"{ram}GB RAM is suitable for basic use"
        )

    # ========================================================
    # STORAGE
    # ========================================================

    storage = get_storage_gb(specs)

    if storage >= requirements["min_storage"]:

        score += 10

        reasons.append(
            f"{storage}GB storage meets the recommended requirement"
        )

    elif storage >= 256:

        score += 5

    # ========================================================
    # CPU
    # ========================================================

    cpu_score = get_cpu_score(specs)

    if cpu_score >= requirements["min_cpu_score"]:

        score += 15

        reasons.append(
            "Processor meets the recommended performance level"
        )

    elif cpu_score > 0:

        score += 7

    # ========================================================
    # GPU
    # ========================================================

    gpu_score = get_gpu_score(specs)

    if requirements["gpu_required"]:

        if gpu_score >= 20:

            score += 15

            reasons.append(
                "Dedicated graphics are suitable for this workload"
            )

        elif gpu_score > 0:

            score += 5

    else:

        if gpu_score >= 20:

            score += 5

    # ========================================================
    # STOCK
    # ========================================================

    if product.stock_quantity > 0:

        score += 5

        reasons.append(
            "Currently in stock"
        )

    # ========================================================
    # FEATURED
    # ========================================================

    if product.is_featured:

        score += 3

    # ========================================================
    # SALE
    # ========================================================

    if product.is_on_sale:

        score += 2

        reasons.append(
            "Currently on sale"
        )

    # ========================================================
    # CAP SCORE AT 100
    # ========================================================

    score = min(
        score,
        100
    )

    # ========================================================
    # LABEL
    # ========================================================

    if score >= 85:

        label = "Excellent Match"

    elif score >= 70:

        label = "Very Good Match"

    elif score >= 55:

        label = "Good Match"

    elif score >= 40:

        label = "Suitable"

    else:

        label = "Basic Match"

    return (
        score,
        label,
        reasons[:5],
    )


# ============================================================
# LAPTOP RECOMMENDATION API
# ============================================================

class LaptopRecommendationAPIView(
    generics.ListAPIView
):

    serializer_class = LaptopRecommendationSerializer

    def get_queryset(self):

        usage_slug = (
            self.request.query_params.get(
                "usage"
            )
        )

        course_slug = (
            self.request.query_params.get(
                "course"
            )
        )

        # ----------------------------------------------------
        # Get ALL available laptops
        # ----------------------------------------------------

        products = list(
            Product.objects
            .filter(
                status="active",
                stock_quantity__gt=0,
                category__slug__iexact="laptops",
            )
            .select_related(
                "category",
                "brand",
            )
            .prefetch_related(
                "images",
                "specifications",
                "usage",
                "courses",
            )
            .distinct()
        )

        # ----------------------------------------------------
        # Score EVERY laptop
        # ----------------------------------------------------

        scored_products = []

        for product in products:

            (
                score,
                label,
                reasons,
            ) = calculate_laptop_score(
                product,
                usage_slug,
                course_slug,
            )

            # Attach temporary recommendation data
            product.recommendation_score = score
            product.recommendation_label = label
            product.recommendation_reasons = reasons

            scored_products.append(
                product
            )

        # ----------------------------------------------------
        # Sort highest score first
        # ----------------------------------------------------

        scored_products.sort(
            key=lambda product: (
                product.recommendation_score,
                product.stock_quantity,
                product.is_featured,
            ),
            reverse=True,
        )

        return scored_products

# ============================================================
# PRODUCT DETAIL
# ============================================================

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
            "usage",
            "courses",
        )
    )

    serializer_class = ProductSerializer

    lookup_field = "slug"


# ============================================================
# RELATED PRODUCTS
# ============================================================

class RelatedProductsAPIView(
    generics.ListAPIView
):
    serializer_class = ProductSerializer

    def get_queryset(self):

        slug = self.kwargs["slug"]

        # Get current product
        try:

            current_product = (
                Product.objects
                .select_related(
                    "category",
                    "brand",
                )
                .get(
                    slug=slug,
                    status="active",
                )
            )

        except Product.DoesNotExist:

            return Product.objects.none()

        # ========================================================
        # SAME CATEGORY
        # ========================================================

        same_category = (
            Product.objects
            .filter(
                status="active",
                category=current_product.category,
            )
            .exclude(
                id=current_product.id
            )
            .select_related(
                "category",
                "brand",
            )
            .prefetch_related(
                "images",
                "specifications",
                "usage",
                "courses",
            )
            .order_by("-created_at")
        )

        # ========================================================
        # ACCESSORIES
        # ========================================================

        accessories = (
            Product.objects
            .filter(
                status="active",
                category__name__icontains="accessor",
            )
            .exclude(
                id=current_product.id
            )
            .select_related(
                "category",
                "brand",
            )
            .prefetch_related(
                "images",
                "specifications",
                "usage",
                "courses",
            )
            .order_by("-created_at")
        )

        # ========================================================
        # COMBINE PRODUCTS
        # ========================================================

        product_ids = set()
        combined_products = []

        # Same category first
        for product in same_category:

            if product.id not in product_ids:

                combined_products.append(
                    product
                )

                product_ids.add(
                    product.id
                )

            if len(combined_products) >= 4:
                break

        # Accessories
        for product in accessories:

            if product.id not in product_ids:

                combined_products.append(
                    product
                )

                product_ids.add(
                    product.id
                )

            if len(combined_products) >= 8:
                break

        return combined_products


# ============================================================
# PRODUCT IMAGE CREATE
# ============================================================

class ProductImageCreateAPIView(
    generics.CreateAPIView
):
    permission_classes = [IsStaffOrAdmin]


    queryset = ProductImage.objects.all()

    serializer_class = ProductImageSerializer


# ============================================================
# PRODUCT SPECIFICATION CREATE
# ============================================================

class ProductSpecificationCreateAPIView(
    generics.CreateAPIView
):
    permission_classes = [IsStaffOrAdmin]


    queryset = ProductSpecification.objects.all()

    serializer_class = ProductSpecificationSerializer


# ============================================================
# ADMIN STORE SETTINGS
# ============================================================

class AdminStoreSettingsAPIView(APIView):
    permission_classes = [IsStaffOrAdmin]


    def get(self, request):

        settings = StoreSettings.objects.first()

        if not settings:

            settings = StoreSettings.objects.create(
                store_name="Anova Technologies",
                country="Kenya",
            )

        serializer = StoreSettingsSerializer(
            settings
        )

        return Response(
            serializer.data
        )

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