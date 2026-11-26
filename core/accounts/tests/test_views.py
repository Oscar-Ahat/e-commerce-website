from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import OTPCode
from django.core.cache import cache

User = get_user_model()

class OTPRequestTests(APITestCase):
    """Request OTP test endpoint"""
    def setUp(self):
        cache.clear()

    def test_request_otp_creates_code(self):
        response = self.client.post('/api/accounts/otp/request/',{
            'email': 'test@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(OTPCode.objects.filter(email='test@example.com').exists())

    def test_request_otp_sends_email(self):
        self.client.post('/api/accounts/otp/request/', {
            'email': 'mail@example.com'
        }, format='json')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('mail@example.com', mail.outbox[0].to)

    def test_request_otp_invalidates_previous(self):
        self.client.post('/api/accounts/otp/request/', {'email': 'x@example.com'}, format='json')
        self.client.post('/api/accounts/otp/request/', {'email': 'x@example.com'}, format='json')

        active = OTPCode.objects.filter(email='x@example.com', is_used=False)
        self.assertEqual(active.count(), 1)


    def test_request_otp_missing_email_fails(self):
        response = self.client.post('/api/accounts/otp/request/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_notmalized_to_lowercase(self):
        self.client.post('/api/accounts/otp/request/', {
            'email': 'UPPER@Example.COM'
        }, format='json')
        self.assertTrue(OTPCode.objects.filter(email='upper@example.com').exists())


class OTPVerifyTests(APITestCase):
    """Verify OTP code"""

    def setUp(self):
        cache.clear()
        self.otp = OTPCode.objects.create(email='verify@example.com')

    def test_verify_returns_tokens(self):
        response = self.client.post('/api/accounts/otp/verify/',{
            'email': 'verify@example.com',
            'code': self.otp.code,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_verify_creates_user(self):
        self.client.post('/api/accounts/otp/verify/', {
            'email': 'verify@example.com',
            'code': self.otp.code,
        }, format='json')

        self.assertTrue(User.objects.filter(email='verify@example.com').exists())

    def test_verify_marks_user_verified(self):
        response = self.client.post('/api/accounts/otp/verify/', {
            'email': 'verify@example.com',
            'code': self.otp.code,
        }, format='json')
        user = User.objects.get(email='verify@example.com')
        self.assertTrue(user.is_verified)
        print('Verify Response:', response.data)

    def test_verify_marks_otp_used(self):
        self.client.post('/api/accounts/otp/verify/', {
            'email': 'verify@example.com',
            'code': self.otp.code,
        }, format='json')

        self.otp.refresh_from_db()
        self.assertTrue(self.otp.is_used)


    def test_wrong_code_fails(self):
        response = self.client.post('/api/accounts/otp/verify/', {
            'email': 'verify@example.com',
            'code': '000000',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reused_otp_fails(self):
        #Used seccussfully
        self.client.post('/api/accounts/otp/verify/', {
            'email': 'verify@example.com',
            'code': self.otp.code,
        }, format='json')
        #it should return an error the second Time 
        response = self.client.post('/api/accounts/otp/verify/', {
            'email': 'verify@example.com',
            'code': self.otp.code,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

