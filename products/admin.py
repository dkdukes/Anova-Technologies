from django.contrib import admin
from . models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSpecification
)
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )
    search_fields = (
        "name"
    )
    prepopulated_fields = {
        "slug":("name",)
    }


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active"
    )
    search_fields = (
        "name"
    )
    prepopulated_fields = {
        "slug":("name",)
    }

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "sale_price",
        "stock_quantity",
        "condition",
        "status",
        "is_featured",
    )
    list_filter = (
        "category",
        "brand",
        "condition",
        "status",
        "is_featured"
    )
    search_fields = (
        "name",
        "sku",
        "brand_name",
        "category_name",
    )
    prepopulated_fields = {
        "slug":("name",)
    }
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = [
        ProductImageInline,
        ProductSpecificationInline
    ]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields" : (
                    "name",
                    "slug",
                    "sku",
                    "category",
                    "brand",
                    "condition",
                    "status"
                )
            },
        ),
        (
            "Description",
            {
                "fields":(
                    "short_description",
                    "description"
                )
            },
        ),
        (
            "Pricing & Inventory",
            {
                "fields":(
                    "price",
                    "sale_price",
                    "stock_quantity",
                    "low_stock_threshold",
                    "warranty"
                )
            },
        ),
        (
            "Delivery Information",
            {
                "fields":(
                    "weight",
                    "package_length",
                    "package_width",
                    "package_height"
                )
            },
        ),
        (
            "SEO",
            {
                "fields",(
                    "meta_title",
                    "meta_description"
                )
            },
        ),
        (
            "Store Settings",
            {
                "fields":(
                    "is_featured"
                )
            },
        ),
        (
            "System Information",
            {
                "fields":(
                    "created_at",
                    "updated_at"
                )
            },
        ),
    )