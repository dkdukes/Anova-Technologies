from rest_framework import serializers

from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    SpecificationTemplate,
    StoreSettings
)


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


class ProductSerializer(
    serializers.ModelSerializer
):

    # Read product category
    category = CategorySerializer(
        read_only=True
    )

    # Accept category ID when creating
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(
            is_active=True
        ),
        source="category",
        write_only=True,
    )

    # Read product brand
    brand = BrandSerializer(
        read_only=True
    )

    # Accept brand ID when creating
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.filter(
            is_active=True
        ),
        source="brand",
        write_only=True,
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    specifications = ProductSpecificationSerializer(
        many=True,
        read_only=True
    )

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

        fields = [

            "id",

            "name",
            "slug",
            "sku",

            "category",
            "category_id",

            "brand",
            "brand_id",

            "short_description",
            "description",
            "highlights",

            "price",
            "sale_price",
            "current_price",

            "stock_quantity",
            "low_stock_threshold",

            "condition",
            "warranty",

            "weight",
            "package_length",
            "package_width",
            "package_height",

            "images",
            "specifications",

            "status",
            "is_featured",

            "meta_title",
            "meta_description",

            "is_on_sale",
            "is_low_stock",

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


class AdminProductSerializer(serializers.ModelSerializer):
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

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    specifications = ProductSpecificationSerializer(
        many=True,
        read_only=True
    )

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

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",

            "name",
            "slug",
            "sku",

            "category",
            "category_id",
            "category_name",

            "brand",
            "brand_id",
            "brand_name",

            "short_description",
            "description",
            "highlights",

            "price",
            "sale_price",
            "current_price",

            "stock_quantity",
            "low_stock_threshold",

            "condition",
            "warranty",

            "weight",
            "package_length",
            "package_width",
            "package_height",

            "images",
            "specifications",

            "status",
            "is_featured",

            "meta_title",
            "meta_description",

            "is_on_sale",
            "is_low_stock",

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


class AdminBrandSerializer(serializers.ModelSerializer):
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

    
class AdminBrandProductSerializer(serializers.ModelSerializer):
    current_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
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


class AdminBrandDetailSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    products = AdminBrandProductSerializer(
        many=True,
        read_only=True,
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

class AdminCategorySerializer(serializers.ModelSerializer):
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


class StoreSettingsSerializer(serializers.ModelSerializer):

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