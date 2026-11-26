from rest_framework import serializers
from .models import Cart, CartItem
from catalog.models import ProductVariant

class CartItemSerializer(serializers.ModelSerializer):
    
    variant_name = serializers.CharField(source='vaiant.product.name', read_only=True)
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)
    product_slug = serializers.CharField(source='variant.product.slug', read_only=True)
    stock = serializers.IntegerField(source='variant.stock', read_only=True)
    row_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'variant', 'variant_name', 'variant_sku', 'product_slug',
            'stock', 'quantity', 'price_at_add', 'row_total', 'added_at',
        ]
        read_only_fields = ['id', 'price_at_add', 'added_at']

    def get_row_total(self, obj):
        return obj.get_cost()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_quantity', 'updated_date']


class AddToCartSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        try:
            variant = ProductVariant.objects.select_related('product').get(
                id=data['variant_id'], is_active=True, product__is_active=True
            )
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("product is inactive or does not exist")

        if variant.stock < data['quantity']:
            raise serializers.ValidationError(
                f"Insufficent balance. Current balance: {variant.stock}"
            )
        
        data['variant'] = variant
        return data
    

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        item = self.context['item']
        if value > item.variant.stock:
            raise serializers.ValidationError(
                f"Insufficent balance. maximum: {item.variant.stock}"
            )
        return value