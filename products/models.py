from django.db import models
from django.utils.text import slugify


# ============================================================
# CATEGORY
# ============================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.URLField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2

            while Product.objects.filter(
                slug=slug
            ).exclude(
                pk=self.pk
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ============================================================
# SPECIFICATION TEMPLATE
# ============================================================

class SpecificationTemplate(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="specification_templates"
    )

    name = models.CharField(
        max_length=100
    )

    is_required = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# ============================================================
# BRAND
# ============================================================

class Brand(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    logo = models.URLField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ============================================================
# USAGE
# ============================================================

class Usage(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ============================================================
# COURSE
# ============================================================

class Course(models.Model):

    usage = models.ForeignKey(
        Usage,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    name = models.CharField(
        max_length=150
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ============================================================
# PRODUCT
# ============================================================

class Product(models.Model):

    # --------------------------------------------------------
    # CONDITION
    # --------------------------------------------------------

    CONDITION_CHOICES = [
        ("new", "New"),
        ("refurbished", "Refurbished"),
    ]

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    STATUS_CHOICES = [
        ("active", "Active"),
        ("draft", "Draft"),
        ("out_of_stock", "Out of Stock"),
        ("archived", "Archived"),
    ]

    # --------------------------------------------------------
    # BASIC PRODUCT INFORMATION
    # --------------------------------------------------------

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        blank=True
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    variation = models.CharField(
        max_length=100,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products"
    )

    # --------------------------------------------------------
    # PRODUCT CLASSIFICATION
    # --------------------------------------------------------

    usage = models.ManyToManyField(
        Usage,
        blank=True,
        related_name="products"
    )

    courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name="products"
    )

    # --------------------------------------------------------
    # PRODUCT DESCRIPTION
    # --------------------------------------------------------

    short_description = models.TextField(
        max_length=500,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    highlights = models.JSONField(
        default=list,
        blank=True
    )

    # --------------------------------------------------------
    # PRODUCT APPEARANCE
    # --------------------------------------------------------

    color = models.CharField(
        max_length=100,
        blank=True
    )

    # --------------------------------------------------------
    # PRICING
    # --------------------------------------------------------

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    sale_start_date = models.DateTimeField(
        blank=True,
        null=True
    )

    sale_end_date = models.DateTimeField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # STOCK
    # --------------------------------------------------------

    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=3
    )

    # --------------------------------------------------------
    # PRODUCT CONDITION & WARRANTY
    # --------------------------------------------------------

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default="new"
    )

    warranty = models.CharField(
        max_length=100,
        blank=True
    )

    # --------------------------------------------------------
    # WEIGHT
    # --------------------------------------------------------

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # PACKAGE DIMENSIONS
    # --------------------------------------------------------

    package_length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    package_width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    package_height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # TECHNICAL SPECIFICATIONS
    # --------------------------------------------------------

    model = models.CharField(
        max_length=150,
        blank=True
    )

    cpu_cores = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    cpu_speed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="CPU speed in GHz"
    )

    display_size = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Display size in inches"
    )

    drive_type = models.CharField(
        max_length=50,
        blank=True
    )

    graphics_type = models.CharField(
        max_length=150,
        blank=True
    )

    storage_capacity = models.CharField(
        max_length=100,
        blank=True
    )

    system_memory = models.CharField(
        max_length=100,
        blank=True
    )

    cpu_manufacturer = models.CharField(
        max_length=100,
        blank=True
    )

    # --------------------------------------------------------
    # SEO
    # --------------------------------------------------------

    # --------------------------------------------------------
    # PRODUCT STATUS
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )


    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:
        ordering = ["-created_at"]

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2

            while Product.objects.filter(
                slug=slug
            ).exclude(
                pk=self.pk
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # --------------------------------------------------------
    # SALE STATUS
    # --------------------------------------------------------

    @property
    def is_on_sale(self):
        """
        Returns True when the product has a valid
        discounted sale price.
        """

        return (
            self.sale_price is not None
            and self.sale_price < self.price
        )

    # --------------------------------------------------------
    # DISCOUNT PERCENTAGE
    # --------------------------------------------------------

    @property
    def discount_percentage(self):
        """
        Calculates the percentage discount between
        the regular price and sale price.
        """

        if (
            self.sale_price is None
            or self.price <= 0
            or self.sale_price >= self.price
        ):
            return 0

        return round(
            ((self.price - self.sale_price) / self.price) * 100,
            2
        )

    # --------------------------------------------------------
    # STOCK STATUS
    # --------------------------------------------------------

    @property
    def is_in_stock(self):
        """
        Returns True when at least one unit is available.
        """

        return self.stock_quantity > 0

    # --------------------------------------------------------
    # LOW STOCK STATUS
    # --------------------------------------------------------

    @property
    def is_low_stock(self):
        """
        Returns True when the product has stock but
        is at or below the configured low-stock threshold.
        """

        return (
            self.stock_quantity > 0
            and self.stock_quantity <= self.low_stock_threshold
        )

    # --------------------------------------------------------
    # STRING REPRESENTATION
    # --------------------------------------------------------

    def __str__(self):
        return self.name


# ============================================================
# PRODUCT IMAGE
# ============================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image_url = models.URLField()

    alt_text = models.CharField(
        max_length=255,
        blank=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


# ============================================================
# PRODUCT SPECIFICATION
# ============================================================

class ProductSpecification(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications"
    )

    name = models.CharField(
        max_length=100
    )

    value = models.TextField()

    sort_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# ============================================================
# STORE SETTINGS
# ============================================================

class StoreSettings(models.Model):

    store_name = models.CharField(
        max_length=255
    )

    store_email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    logo = models.URLField(
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.store_name