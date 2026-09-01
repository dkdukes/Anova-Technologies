from rest_framework import serializers
from . models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    SpecificationTemplate,
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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image_url",
            "alt_text",
            "is_primary",
            "sort_order",
        ]


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = [
            "id",
            "name",
            "value",
            "sort_order",
        ]


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source="category",
        write_only=True,
    )

    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.filter(is_active=True),
        source="brand",
        write_only=True,
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )

    specifications = ProductSpecificationSerializer(
        many=True,
        read_only=True,
    )

    current_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    is_on_sale = serializers.BooleanField(
        read_only=True,
    )

    is_low_stock = serializers.BooleanField(
        read_only=True,
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

    def validate(self, attrs):

        price = attrs.get("price")
        sale_price = attrs.get("sale_price")

        if (
            sale_price is not None
            and price is not None
            and sale_price > price
        ):
            raise serializers.ValidationError(
                {
                    "sale_price":
                    "Sale price cannot be greater than the regular price."
                }
            )

        return attrs