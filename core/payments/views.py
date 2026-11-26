from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

from django_iranian_payment.contrib.django import services
from orders.models import Order
from .models import Payment
from .serializers import PaymentRequestSerializer, PaymentDetailSerializer

class PaymentRequestView(APIView):
    """
    POST /api/payments/request/
    Body: {'order_id': 1}
    The amount is retrieved from the order itself(payable_amount).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaymentRequestSerializer,
        responses={200: inline_serializer(
            name='PaymentInitResponse',
            fields={
                'payment_id': drf_serializers.IntegerField(),
                'redirect_url': drf_serializers.CharField(),
            },
        )},
    )
    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(
            Order,
            id=serializer.validated_data['order_id'],
            user=request.user,
        )

        if order.status == Order.Status.PAID:
            return Response(
                {"detail": "This order has already been paid for."},
                status=status.HTTP_400_BAD_REQUEST,
           )
        
        # Creating a local payment record to maintain the association
        payment = Payment.objects.create(
            order=order,
            gateway=Payment.GateWay.ZARINPALL,
            amount=order.payable_amount,
            status=Payment.Status.PENDING,
        )

        payment_record, redirect_url = services.start_payment(
            "zarinpal",
            amount=int(order.payable_amount), #its converting to rial
            callback_url=request.build_absolute_uri(
                '/payment/callback/zarinpal/' # callback route
            ),
            return_url=request.build_absolute_uri(
                '/api/payments/result/'
            ),
            order_id=str(order.id),
            description=f"Order Payment #{order.id}",
            mobile=order.receiver_phone,
        )

        payment.authority = payment_record.authority
        payment.save(update_fields=['authority'])

        return Response({
            'payment_id': payment.id,
            'redirect_url': redirect_url,
        }, status=status.HTTP_200_OK)

class PaymentResultView(APIView):
    """GET /api/payments/result/?payment_status=success&order_id=1"""
    permission_classes = [AllowAny]

    def get(self, request):
        order_id = request.query_params.get('order_id')
        payment_status = request.query_params.get('payment_status')
        payment = Payment.objects.filter(order_id=order_id).order_by('created_date').first()

        if payment_status == 'success' and payment:
            if payment.status != Payment.Status.SUCCESS:
                payment.status = Payment.Status.SUCCESS
                payment.save(update_fields=['status'])
            
            order=payment.order
            if order.status != order.Status.PAID:
                order.status = order.Status.PAID
                order.save(update_fields=['status'])   

        return Response({
            'order_id': order_id,
            'payment_status': payment_status,
            'payment': PaymentDetailSerializer(payment).data if payment else None,
        })

