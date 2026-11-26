from rest_framework import serializers
from .models import Payment

class PaymentRequestSerializer(serializers.Serializer):
    """Payment request input"""
    order_id = serializers.IntegerField()

class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'gateway', 'amount',
            'authority', 'reference_id', 'status',
            'created_date', 'paid_date'
        ]