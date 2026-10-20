from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('variant', 'quantity', 'price_at_add', 'added_at')
    readonly_fields = ('added_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'total_quantity',
                    'total_price', 'updated_date')
    list_filter = ('created_date', 'updated_date')
    search_fields = ('user__email', 'session_key')
    list_select_related = ('user',)
    readonly_fields = ('created_date', 'updated_date')
    


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'variant' , 'quantity',
                    'price_at_add', 'row_total', 'added_at')
    search_fields = ('cart__user__email', 'variant__sku', 'variant__product__name')
    list_select_related = ('cart', 'variant')
    readonly_fields = ('added_at',)

    @admin.display(description='Row total')
    def row_total(self, obj):
        return obj.get_cost()