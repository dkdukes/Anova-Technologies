from django.urls import path

from .views import (
    CategoryListAPIView,
    BrandListAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductImageCreateAPIView,
    ProductSpecificationCreateAPIView,
    SpecificationTemplateListAPIView,

    AdminProductListAPIView,
    AdminProductDetailAPIView,
    AdminDashboardStatsAPIView,

    AdminCategoryListCreateAPIView,
    AdminCategoryDetailAPIView,
    CategoryImageUploadAPIView,

    AdminBrandListCreateAPIView,
    AdminBrandDetailAPIView,
    BrandLogoUploadAPIView,

    AdminProductImageListCreateAPIView,
    AdminProductImageDetailAPIView,
    AdminProductImageUploadAPIView,
    AdminProductImageReplaceAPIView,
    AdminStoreSettingsAPIView
)


urlpatterns = [

    # ==========================================
    # PUBLIC CATEGORIES
    # ==========================================

    path(
        "categories/",
        CategoryListAPIView.as_view(),
        name="category-list",
    ),

    # ==========================================
    # ADMIN CATEGORIES
    # ==========================================

    path(
        "admin/categories/",
        AdminCategoryListCreateAPIView.as_view(),
        name="admin-category-list-create",
    ),

    path(
        "admin/categories/image-upload/",
        CategoryImageUploadAPIView.as_view(),
        name="admin-category-image-upload",
    ),

    path(
        "admin/categories/<int:pk>/",
        AdminCategoryDetailAPIView.as_view(),
        name="admin-category-detail",
    ),

    # ==========================================
    # BRANDS
    # ==========================================

    path(
        "brands/",
        AdminBrandListCreateAPIView.as_view(),
        name="admin-brand-list-create",
    ),

    path(
        "brands/logo-upload/",
        BrandLogoUploadAPIView.as_view(),
        name="brand-logo-upload",
    ),

    path(
        "brands/<int:pk>/",
        AdminBrandDetailAPIView.as_view(),
        name="admin-brand-detail",
    ),

    # ==========================================
    # SPECIFICATION TEMPLATES
    # ==========================================

    path(
        "specification-templates/",
        SpecificationTemplateListAPIView.as_view(),
        name="specification-template-list",
    ),

    # ==========================================
    # PUBLIC PRODUCT IMAGES
    # ==========================================

    path(
        "products/images/",
        ProductImageCreateAPIView.as_view(),
        name="product-image-create",
    ),

    # ==========================================
    # PUBLIC PRODUCT SPECIFICATIONS
    # ==========================================

    path(
        "products/specifications/",
        ProductSpecificationCreateAPIView.as_view(),
        name="product-specification-create",
    ),

    # ==========================================
    # ADMIN PRODUCTS
    # ==========================================

    path(
        "admin/products/",
        AdminProductListAPIView.as_view(),
        name="admin-product-list",
    ),

    path(
        "admin/products/<int:pk>/",
        AdminProductDetailAPIView.as_view(),
        name="admin-product-detail",
    ),

    # ==========================================
    # ADMIN PRODUCT IMAGES
    # ==========================================

    path(
        "admin/products/<int:product_id>/images/",
        AdminProductImageListCreateAPIView.as_view(),
        name="admin-product-image-list-create",
    ),

    path(
        "admin/products/<int:product_id>/images/upload/",
        AdminProductImageUploadAPIView.as_view(),
        name="admin-product-image-upload",
    ),

    path(
        "admin/products/<int:product_id>/images/<int:pk>/replace/",
        AdminProductImageReplaceAPIView.as_view(),
        name="admin-product-image-replace",
    ),

    path(
        "admin/products/<int:product_id>/images/<int:pk>/",
        AdminProductImageDetailAPIView.as_view(),
        name="admin-product-image-detail",
    ),

    # ==========================================
    # PUBLIC PRODUCTS
    # ==========================================

    path(
        "products/",
        ProductListAPIView.as_view(),
        name="product-list",
    ),

    path(
        "products/<slug:slug>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),

    # ==========================================
    # ADMIN DASHBOARD
    # ==========================================

    path(
        "admin/dashboard/stats/",
        AdminDashboardStatsAPIView.as_view(),
        name="admin-dashboard-stats",
    ),


    path(
    "admin/settings/",
    AdminStoreSettingsAPIView.as_view(),
    name="admin-store-settings",
),
]