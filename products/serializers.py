from rest_framework import serializers

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


# ============================================================
# USAGE SERIALIZER
# ============================================================

class UsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usage

        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]


# ============================================================
# COURSE SERIALIZER
# ============================================================

class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course

        fields = [
            "id",
            "name",
            "slug",
            "usage",
            "description",
        ]


# ============================================================
# CATEGORY SERIALIZER
# ============================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "is_active",
        ]


# ============================================================
# BRAND SERIALIZER
# ============================================================

class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand

        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "is_active",
        ]


# ============================================================
# PRODUCT IMAGE SERIALIZER
# ============================================================

class ProductImageSerializer(
    serializers.ModelSerializer
):

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True,
    )

    class Meta:
        model = ProductImage

        fields = [
            "id",
            "product_id",
            "image_url",
            "alt_text",
            "is_primary",
            "sort_order",
        ]

        read_only_fields = [
            "id",
        ]


# ============================================================
# PRODUCT SPECIFICATION SERIALIZER
# ============================================================

class ProductSpecificationSerializer(
    serializers.ModelSerializer
):

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True,
    )

    class Meta:
        model = ProductSpecification

        fields = [
            "id",
            "product_id",
            "name",
            "value",
            "sort_order",
        ]

        read_only_fields = [
            "id",
        ]


# ============================================================
# SPECIFICATION TEMPLATE SERIALIZER
# ============================================================

class SpecificationTemplateSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = SpecificationTemplate

        fields = [
            "id",
            "name",
            "is_required",
            "sort_order",
        ]


# ============================================================
# PRODUCT SERIALIZER
# ============================================================

class ProductSerializer(
    serializers.ModelSerializer
):

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category = CategorySerializer(
        read_only=True
    )

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(
            is_active=True
        ),
        source="category",
        write_only=True,
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    brand = BrandSerializer(
        read_only=True
    )

    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.filter(
            is_active=True
        ),
        source="brand",
        write_only=True,
    )

    # --------------------------------------------------------
    # IMAGES
    # --------------------------------------------------------

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # SPECIFICATIONS
    # --------------------------------------------------------

    specifications = ProductSpecificationSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # USAGE
    # --------------------------------------------------------

    usage = UsageSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # COURSES
    # --------------------------------------------------------

    courses = CourseSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # PRODUCT CALCULATED FIELDS
    # --------------------------------------------------------

    current_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    is_on_sale = serializers.BooleanField(
        read_only=True
    )

    is_low_stock = serializers.BooleanField(
        read_only=True
    )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:
        model = Product

        fields = [

            "id",

            "name",
            "slug",
            "sku",

            # Category
            "category",
            "category_id",

            # Brand
            "brand",
            "brand_id",

            # Description
            "short_description",
            "description",
            "highlights",

            # Pricing
            "price",
            "sale_price",
            "current_price",

            # Stock
            "stock_quantity",
            "low_stock_threshold",

            # Product condition
            "condition",
            "warranty",

            # Package information
            "weight",
            "package_length",
            "package_width",
            "package_height",

            # Usage / Courses
            "usage",
            "courses",

            # Images / Specifications
            "images",
            "specifications",

            # Status
            "status",
            "is_featured",

            # SEO
            "meta_title",
            "meta_description",

            # Calculated
            "is_on_sale",
            "is_low_stock",

            # Dates
            "created_at",
            "updated_at",
        ]

        read_only_fields = [

            "id",
            "slug",

            "current_price",
            "is_on_sale",
            "is_low_stock",

            "created_at",
            "updated_at",
        ]


# ============================================================
# LAPTOP RECOMMENDATION SERIALIZER
# ============================================================

class LaptopRecommendationSerializer(ProductSerializer):

    recommendation_score = serializers.IntegerField(
        read_only=True
    )

    recommendation_label = serializers.CharField(
        read_only=True
    )

    recommendation_reasons = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            "recommendation_score",
            "recommendation_label",
            "recommendation_reasons",
        ]


# ============================================================
# ADMIN PRODUCT SERIALIZER
# ============================================================

class AdminProductSerializer(
    serializers.ModelSerializer
):

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category = CategorySerializer(
        read_only=True
    )

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(
            is_active=True
        ),
        source="category",
        write_only=True,
        required=False,
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    brand = BrandSerializer(
        read_only=True
    )

    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.filter(
            is_active=True
        ),
        source="brand",
        write_only=True,
        required=False,
    )

    # --------------------------------------------------------
    # IMAGES
    # --------------------------------------------------------

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # SPECIFICATIONS
    # --------------------------------------------------------

    specifications = ProductSpecificationSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # USAGE
    # --------------------------------------------------------

    usage = UsageSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # COURSES
    # --------------------------------------------------------

    courses = CourseSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # CALCULATED FIELDS
    # --------------------------------------------------------

    current_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    is_on_sale = serializers.BooleanField(
        read_only=True
    )

    is_low_stock = serializers.BooleanField(
        read_only=True
    )

    # --------------------------------------------------------
    # DISPLAY FIELDS
    # --------------------------------------------------------

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True
    )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:
        model = Product

        fields = [

            "id",

            "name",
            "slug",
            "sku",

            # Category
            "category",
            "category_id",
            "category_name",

            # Brand
            "brand",
            "brand_id",
            "brand_name",

            # Description
            "short_description",
            "description",
            "highlights",

            # Pricing
            "price",
            "sale_price",
            "current_price",

            # Stock
            "stock_quantity",
            "low_stock_threshold",

            # Product condition
            "condition",
            "warranty",

            # Package information
            "weight",
            "package_length",
            "package_width",
            "package_height",

            # Usage / Courses
            "usage",
            "courses",

            # Images / Specifications
            "images",
            "specifications",

            # Status
            "status",
            "is_featured",

            # SEO
            "meta_title",
            "meta_description",

            # Calculated
            "is_on_sale",
            "is_low_stock",

            # Dates
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",

            "current_price",
            "is_on_sale",
            "is_low_stock",

            "created_at",
            "updated_at",
        ]


# ============================================================
# ADMIN BRAND SERIALIZER
# ============================================================

class AdminBrandSerializer(
    serializers.ModelSerializer
):

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand

        fields = (
            "id",
            "name",
            "slug",
            "logo",
            "is_active",
            "product_count",
        )

        read_only_fields = (
            "id",
            "slug",
            "product_count",
        )

    def get_product_count(self, obj):
        return obj.products.count()


# ============================================================
# ADMIN BRAND PRODUCT SERIALIZER
# ============================================================

class AdminBrandProductSerializer(
    serializers.ModelSerializer
):

    current_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    is_on_sale = serializers.BooleanField(
        read_only=True
    )

    is_low_stock = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = Product

        fields = (
            "id",
            "name",
            "slug",
            "sku",
            "price",
            "sale_price",
            "current_price",
            "stock_quantity",
            "low_stock_threshold",
            "status",
            "is_featured",
            "is_on_sale",
            "is_low_stock",
        )


# ============================================================
# ADMIN BRAND DETAIL SERIALIZER
# ============================================================

class AdminBrandDetailSerializer(
    serializers.ModelSerializer
):

    product_count = serializers.SerializerMethodField()

    products = AdminBrandProductSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Brand

        fields = (
            "id",
            "name",
            "slug",
            "logo",
            "is_active",
            "product_count",
            "products",
        )

        read_only_fields = (
            "id",
            "slug",
            "product_count",
            "products",
        )

    def get_product_count(self, obj):
        return obj.products.count()


# ============================================================
# ADMIN CATEGORY SERIALIZER
# ============================================================

class AdminCategorySerializer(
    serializers.ModelSerializer
):

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category

        fields = (
            "id",
            "name",
            "slug",
            "description",
            "image",
            "is_active",
            "product_count",
            "created_at",
        )

        read_only_fields = (
            "id",
            "slug",
            "product_count",
            "created_at",
        )

    def get_product_count(self, obj):
        return obj.products.count()


# ============================================================
# STORE SETTINGS SERIALIZER
# ============================================================

class StoreSettingsSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = StoreSettings

        fields = [
            "id",
            "store_name",
            "store_email",
            "phone",
            "address",
            "city",
            "country",
            "logo",
            "description",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "updated_at",
        ]