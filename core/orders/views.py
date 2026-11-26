from decimal import Decimal
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db import transaction

from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CheckoutSerializer,
)
from catalog.models import ProductVariant

class OrderViewSet(ReadOnlyModelViewSet):
    """View only the current user's orders"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

class CheckoutView(APIView):
    """
    POST /api/orders/checkout/
    Converting Shopping Cart to Order + Reducing Inventry
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CheckoutSerializer,
        responses={201: OrderDetailSerializer},
        description="Convert the current cart into an order.",
    )
    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        cart = data['cart']

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                receiver_name=data['receiver_name'],
                province=data['province'],
                city=data['city'],
                postal_code=data['postal_code'],
                full_address=data['full_address'],
                note=data.get('note', ''),
                shipping_cost=data.get('shipping_cost', Decimal('0')),
                total_price=Decimal('0'),
                status=Order.Status.PENDING,
            )

            total_price = Decimal('0')

            for item in list(cart.items.all()):
                variant = ProductVariant.objects.select_for_update().get(
                    pk=item.variant_id
                )
                if variant.stock < item.quantity:
                    raise serializers.ValidationError(
                        f"There is insufficient stock of this '{variant.product.name}'"
                    )
                
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    product_name=variant.product.name,
                    quantity=item.quantity,
                    unit_price=item.price_at_add,
                )
                total_price += item.price_at_add * item.quantity

                variant.stock -= item.quantity
                variant.save(update_fields=['stock'])

            order.total_price = total_price
            order.save(update_fields=['total_price'])
            cart.items.all().delete()
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )