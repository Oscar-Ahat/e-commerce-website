from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from orders.models import Order
from payments.models import Payment

User = get_user_model()

class PaymentAPITests(APITestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            email='pay_user@example.com',
            password='password123'
        )

        self.order = Order.objects.create(
            user=self.user,
            receiver_name='Test User',
            province='Tehran', city='Tehran',
            postal_code='1234567890', full_address='Test Addr',
            total_price=100000,
            status=Order.Status.PENDING
        )

    def test_guest_cannot_request_payment(self):
        """guest user should not to payment request user"""
        response = self.client.post('/api/payments/request/', {'order_id': self.order.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pay_already_paid_order_fails(self):
        self.client.force_authenticate(user=self.user,)
        self.order.status = Order.Status.PAID
        self.order.save()

        response = self.client.post('/api/payments/request/', {'order_id': self.order.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('payments.views.services.start_payment')
    def test_succesful_payment_request(self, mock_start_payment):

        # Fake response for Zarinpal
        mock_record = MagicMock()
        mock_record.authority = 'TEST-AUTH-123'
        fake_redirect_url = 'https://sandbox.zarinpal.com/pay/TEST-AUTH-123'
        # Return value
        mock_start_payment.return_value = (mock_record, fake_redirect_url)
        # Login and request
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/payments/request/', {'order_id': self.order.id}, format='json')
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['redirect_url'], fake_redirect_url)
        # Check for create record and payment
        self.assertTrue(Payment.objects.filter(order=self.order).exists())
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.authority, 'TEST-AUTH-123')
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_payment_result_marks_order_as_paid(self):
        """Testing the return from the payment gateway and status update"""
        payment = Payment.objects.create(
            order=self.order, gateway=Payment.GateWay.ZARINPALL,
            amount=100000, status=Payment.Status.PENDING
        )

        response = self.client.get(f'/api/payments/result/?payment_status=success&order_id={self.order.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertEqual(payment.status, Payment.Status.SUCCESS)

