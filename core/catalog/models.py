from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=200, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name="child", null=True, 
        blank=True, verbose_name="parent category")
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:category-detail', kwargs={'slug': self.slug})
    
class Brand(models.Model):
    """Product Brand"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
        

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='product')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class meta:
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active'])
        ]

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    """Each Product can have several Images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='proudcts/')
    alt_text = models.CharField(max_length=150, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-is_main', 'order']


class ProductVariant(models.Model):
    """Variants of Product(size/color)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField('storage code (sku)', max_length=64, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True, help_text='{"size": "XL", "color": "Red"}')
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'is_active'])
        ]

    def __str__(self):
        attrs = ', '.join(f'{k}:{v}' for k, v in self.attributes.items())
        return f'{self.product.name} - {attrs or self.sku}'
