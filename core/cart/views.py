from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer
    )

def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

class CartView(APIView):
    """
    GET /api/cart/ ->  see the cart
    DELETE /api/cart/ -> empty shop cart
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CartSerializer})
    def get(self, request):
        cart = get_user_cart(request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    @extend_schema(responses={204: OpenApiResponse(description="Cart emtied.")})
    def delete(self, request):
        cart = get_user_cart(request.user)
        cart.items.all().delete()
        return Response(
            {"detail": "The shopping cart has been emptied."},
            status=status.HTTP_204_NO_CONTENT
        )
    
class CartItemAddView(APIView):
    """
    POST /api/cart/items/
    Body: {"variant_id": 1, "quantity":2}
    if the item was already in the cart, the quantity increases.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
            request=AddToCartSerializer,
            responses={
                201: CartItemSerializer,
                200: CartItemSerializer,
            },
            description="Add a variant to cart. Increases quantity if already present.",
    )

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant = serializer.validated_data['variant']
        quantity = serializer.validated_data['quantity']

        cart = get_user_cart(request.user)
        # for avoiding of race condition
        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(
                cart= cart,
                variant= variant,
                defaults={'quantity': quantity, 'price_at_add': variant.price},
            )

            if not created:
                new_qty = item.quantity + quantity
                if new_qty > variant.stock:
                    return Response(
                        {"detail": f"The total quantity exceeds the available stock. maximiu{variant.stock}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity = new_qty
                item.save()

        response_serializer = CartItemSerializer(item)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )


class CartItemDetailView(APIView):
    """
    PATCH api/cart/items/{id}/ -> changing quantity
    DELETE api/cart/items/{id}/ -> deleting item
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(CartItem, id=pk, cart__user=request.user)

    @extend_schema(request=UpdateCartItemSerializer, responses={200: CartItemSerializer})
    def patch(self, request, pk):
        item = self.get_object(request, pk)
        serializer = UpdateCartItemSerializer(
            data=request.data, context={'item': item}
        )
        serializer.is_valid(raise_exception=True)
        item.quantity = serializer.validated_data['quantity']
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, pk):
        item = self.get_object(request, pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    