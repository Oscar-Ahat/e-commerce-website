from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductVariant
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent', 'is_active', 'created_date')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    list_select_related = ('parent',)
    readonly_fields = ('created_date',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'is_active', 'logo_preview')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;" />', obj.logo.url)
        return '-'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'order')
    ordering = ('-is_main', 'order')

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extar = 1
    fields = ('sku', 'price', 'stock', 'attributes', 'is_active')
    show_change_link = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    list_display = (
        'id', 'name', 'slug', 'category', 'brand', 'base_price',
        'is_active', 'variant_count', 'created_date'
    )
    list_filter = ('is_active', 'category', 'brand', 'created_date')
    search_fields = ('name', 'slug', 'brand__name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    list_select_related = ('category', 'brand')
    readonly_fields = ('created_date', 'updated_date')
    date_hierarchy = 'created_date'
    autocomplete_fields = ('category', 'brand')

    @admin.display(description='Variants')
    def variant_count(self, obj):
        return obj.variants.count()

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_preview', 'is_main', 'order')
    list_filter = ('is_main',)
    search_fields = ('product__name',)
    list_select_related = ('product',)

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;" />', obj.image.url)
        return '-'
    

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'sku', 'price', 'stock',
                     'is_active', 'created_date')
    list_fileter = ('is_active', 'created_date')
    search_fields = ('sku', 'product__name')
    list_select_related = ('product',)
    list_editable = ('price', 'stock', 'is_active')
    readonly_fields = ('created_date',)
    