from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTPCode

User = get_user_model()

class RequestOTPSerializer(serializers.Serializer):
    """Receive email and send OTP"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        # Normalize email to lowercase
        return value.lower()

class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP and recieve JWT tokens"""
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length= 6)

    def validate(self, data):
        email = data['email'].lower()
        code = data['code']

        try:
            otp = OTPCode.objects.filter(
                email=email, code=code, is_used=False,
                ).latest('created_at')
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired code")

        if not otp.is_valid():
            raise serializers.ValidationError("Code has expired.")

        # Attach OTP to validated_data for use in view
        data['otp'] = otp
        data['email'] = email
        return data