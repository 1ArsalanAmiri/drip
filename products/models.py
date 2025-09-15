from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid

def unique_slugify(instance, value, slug_field_name='slug', queryset=None, slug_separator='-'):
    slug = slugify(value)
    ModelClass = instance.__class__
    if queryset is None:
        queryset = ModelClass.objects.all()
    slug_candidate = slug
    i = 1
    while queryset.filter(**{slug_field_name: slug_candidate}).exclude(pk=getattr(instance, 'pk', None)).exists():
        slug_candidate = f"{slug}{slug_separator}{i}"
        i += 1
    return slug_candidate

# ---------- Category ----------
class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

# ---------- Tag ----------
class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=40, unique=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

# ---------- Product ----------
def product_image_upload_to(instance, filename):
    slug = instance.product.slug or 'product'
    name = f"{uuid.uuid4().hex[:8]}-{filename}"
    return f"products/{slug}/{name}"

class Product(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ('-is_featured', '-created_at')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_main_image(self):
        img = self.images.order_by('order').first()
        return img.image.url if img else None

    def get_price_range(self):
        return (self.base_price, self.base_price)

    @property
    def url(self):
        return f"/products/{self.slug}/"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_to)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ('order',)
        indexes = [
            models.Index(fields=['product', 'order']),
        ]

    def __str__(self):
        return f"Image for {self.product.name} ({self.order})"

# ---------- Collection ----------
class Collection(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    teaser_image = models.ImageField(upload_to='collections/', blank=True, null=True)
    products = models.ManyToManyField(Product, related_name='collections', blank=True)
    is_active = models.BooleanField(default=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-start_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def is_live(self):
        now = timezone.now()
        if self.start_at and self.end_at:
            return self.start_at <= now <= self.end_at
        if self.start_at and not self.end_at:
            return self.start_at <= now
        return self.is_active

# ---------- Event ----------
class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    banner = models.ImageField(upload_to='events/', blank=True, null=True)
    collections = models.ManyToManyField(Collection, related_name='events', blank=True)
    products = models.ManyToManyField(Product, related_name='events', blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ('-start_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def status(self):
        now = timezone.now()
        if now < self.start_at:
            return 'upcoming'
        if self.start_at <= now <= self.end_at:
            return 'live'
        return 'ended'
