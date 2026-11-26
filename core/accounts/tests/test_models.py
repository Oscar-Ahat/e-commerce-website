from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import OTPCode, Address

User = get_user_model()

class OTPCodeModelTests(TestCase):

    def test_auto_generates_code(self):
        otp = OTPCode.objects.create(email='a@example.com')
        self.assertEqual(len(otp.code), 6)
        self.assertTrue(otp.code.isdigit())

    def test_auto_sets_expiry(self):
        otp = OTPCode.objects.create(email='a@example.com')
        self.assertIsNotNone(otp.expires_at)
        self.assertGreater(otp.expires_at, timezone.now())
    
    def test_valid_when_fresh(self):
        otp = OTPCode.objects.create(email='a@exmaple.com')
        self.assertTrue(otp.is_valid())

    def test_invalid_when_used(self):
        otp = OTPCode.objects.create(email='a@exmaple.com')
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        self.assertFalse(otp.is_valid())

class AddressModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='addr@example.com', password='testpass123'
        )

    def test_default_address_unsetss_others(self):
        a1 = Address.objects.create(
            user=self.user, title='Home', receiver_name='X',
            province='Tehran', city='Tehran', postal_code='1234567890',
            full_address='Addr 1', is_default=True,
        )
        a2 = Address.objects.create(
            user=self.user, title='Work', receiver_name='Y',
            province='Tehran', city='Tehran', postal_code='1234567890',
            full_address='Addr 2', is_default=True,
        )
        a1.refresh_from_db()
        self.assertFalse(a1.is_default)
        self.assertTrue(a2.is_default)