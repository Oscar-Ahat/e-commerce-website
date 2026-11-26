from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem
from accounts.models import Address

class OrderItemSerializer(serializers.ModelSerializer):
    row_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'product_name', 'quantity', 'unit_price', 'row_total']

    def get_row_total(self, obj):
        return obj.get_cost()

class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'total_price',
            'shipping_cost', 'discount', 'payable_amount',
            'item_count', 'created_date',
        ]

    def get_item_count(self, obj):
        return obj.items.count()

class OrderDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 
            'receiver_name', 'province', 'city',
            'postal_code', 'full_address', 'total_price',
            'shipping_cost', 'discount', 'note', 'items',
            'item_count', 'created_date', 'updated_date',
        ]
    def get_item_count(self, obj):
        return obj.items.count()

class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False)    
    receiver_name = serializers.CharField(max_length=100, required=False)
    province = serializers.CharField(max_length=50, required=False)
    city = serializers.CharField(max_length=50, required=False)
    postal_code = serializers.CharField(max_length=10, required=False)
    full_address = serializers.CharField(required=False)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    shipping_cost = serializers.DecimalField(
        max_digits=12, decimal_places=0, required=False, default=Decimal('0')
    )

    def validate(self, data):
        user = self.context['request'].user

        if data.get('address_id'):
            try:
                address = Address.objects.get(id=data['address_id'], user=user)
            except Address.DoesNotExist:
                raise serializers.ValidationError({"address_id": "Address does not found."})

            data['receiver_name'] = address.receiver_name
            data['province']= address.province
            data['city'] = address.city
            data['postal_code'] = address.postal_code
            data['full_address'] = address.full_address

        else:
            for field in ['receiver_name', 'province', 'city', 'postal_code', 'full_address']:
                if not data.get(field):
                    raise serializers.ValidationError({field: "This field required."})

        cart = getattr(user, 'cart', None)
        if not cart or not cart.items.exists():
            raise serializers.ValidationError("The cart is empty.")

        for item in cart.items.select_related('variant', 'variant__product'):
            if item.quantity > item.variant.stock:
                raise serializers.ValidationError(
                    f"There is insufficient stock of this '{item.variant.product.name}'"
                )
        
        data['cart'] = cart
        return data