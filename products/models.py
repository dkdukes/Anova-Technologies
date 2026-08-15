from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):

    CONDITION_CHOICES = [
        ("new", "New"),
        ("refurbished", "Refurbished"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("draft", "Draft"),
        ("out_of_stock", "Out of Stock"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=280,
        unique=True,
        blank=True
    )

    sku = models.CharField(
        max_length=100,
        unique=True
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

    short_description = models.TextField(
        max_length=500,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

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

    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=3
    )

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default="new"
    )

    warranty = models.CharField(
        max_length=100,
        blank=True
    )

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Weight in kilograms"
    )

    package_length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Length in centimeters"
    )

    package_width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Width in centimeters"
    )

    package_height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Height in centimeters"
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    is_featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def current_price(self):
        if self.sale_price is not None:
            return self.sale_price
        return self.price

    @property
    def is_on_sale(self):
        return (
            self.sale_price is not None
            and self.sale_price < self.price
        )

    @property
    def is_low_stock(self):
        return (
            self.stock_quantity > 0
            and self.stock_quantity <= self.low_stock_threshold
        )

    def __str__(self):
        return self.name


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
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.product.name} - Image"


class ProductSpecification(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications"
    )

    name = models.CharField(
        max_length=100
    )

    value = models.CharField(
        max_length=255
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name}: {self.value}"