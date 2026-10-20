from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('variant', 'product_name', 'quantity',
             'unit_price', 'row_total')
    readonly_fields = ('row_total',)
    raw_id_fields = ('variant',)

    @admin.display(description='Row total')
    def row_total(self, obj):
        if obj.pk:
            return obj.get_cost()
        return '-'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = (
        'id', 'user', 'receiver_name', 'status_badge',
        'total_price', 'shipping_cost', 'discount',
        'payable_amount', 'created_date'
    )
    list_filter = ('status', 'created_date', 'province')
    search_fields = ('id', 'user__email', 'receiver_name', 'postal_code')
    list_select_related = ('user',)
    readonly_fields = ('created_date', 'updated_date', 'payable_amount')
    date_hierarchy = 'created_date'
    list_per_page = 30
    actions = ['mark_as_paid', 'mark_as_shipped']

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12',
            'paid': '#27ae60',
            'processing': '#2980b9',
            'shipped': '#8e44ad',
            'delivered': '#16a085',
            'canceled': '#c0392b',
            'refunded': '#7f8c8d',
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background:{};color:#fff;pending;3px 8px;'
            'border-radius:4px;font-size:12px;">{}</span>',
            color, obj.get_status_display()
        )
    
    @admin.action(description='Mark selected orders as paid')
    def mark_as_paid(self, request, queryset):
        queryset.update(status=Order.Status.PAID)

    @admin.action(description='Mark selected orders as shipped')
    def mark_as_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'product_name', 'variant',
        'quantity', 'unit_price', 'row_total'
    )
    search_fields = ('order_id', 'product_name', 'variant__sku')
    list_select_related = ('order', 'variant')
    raw_id_fields = ('order', 'variant')


    @admin.display(description='Row total')
    def row_total(self, obj):
        return obj.get_cost()