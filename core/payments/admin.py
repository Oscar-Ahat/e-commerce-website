from django.contrib import admin
from django.utils.html import format_html
from .models import Payment
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order_link', 'gateway', 'amount',
        'status_badge', 'authority', 'reference_id',
        'created_date', 'paid_date'
    )
    list_filter = ('status', 'gateway', 'created_date')
    search_fields = ('order__id', 'authority', 'transaction_id')
    list_select_related = ('order',)
    readonly_fields = ('created_date', 'gateway_response')
    date_hierarchy = 'created_date'
    list_per_page = 30

    @admin.display(description='Order', ordering='order__id')
    def order_link(self, obj):
        return format_html(
            '<a href="admin/orders/order/{}/change">#{}</a>',
            obj.order_id, obj.order_id
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12',
            'success': '#27ae60',
            'failed': '#c0392b',
            'canceled': '#7f8c8d',
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background:{};color:#fff;pending;3px 8px;'
            'border-radius:4px;font-size:12px;">{}</span>',
            color, obj.get_status_display()
        )
        