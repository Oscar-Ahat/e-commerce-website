from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import OTPCode
from .serializers import RequestOTPSerializer,VerifyOTPSerializer
from .tasks import send_otp_email

User = get_user_model()

class RequestOTPView(APIView):
    """
    POST /api/accounts/otp/request/
    Body: {"email": "user@example.com"}
    Sends a 6-digit OTP to the given email.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_request' # Rate limit: e.g. 3/hour

    @extend_schema(
            request=RequestOTPSerializer,
            responses={200: OpenApiResponse(description="verification code sent.")},
            description="Send a 6-digit OTP to the given email address.",
    )

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Invalidate previous unused OTPs for this email
        OTPCode.objects.filter(email=email, is_used=False).update(is_used=True)
        # Create new OTP
        otp = OTPCode.objects.create(email=email)
        # Send email asynchronously via Celery
        send_otp_email.delay(email, otp.code)

        return Response(
            {"detail": "Verification code sent to your email."},
            status = status.HTTP_200_OK
        )
    
class VerifyOTPView(APIView):
    """
    
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_verify' # Separate scope from login throrrle

    @extend_schema(
            request=VerifyOTPSerializer,
            responses={200: OpenApiResponse(description="JWT tokens returned.")},
            description="Verify OTP and receive access/refresh JWT tokens.",
    )

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data['otp']
        email = serializer.validated_data['email']

        # Invalidate OTP immediately after successful use
        otp.is_used = True
        otp.save()

        # Get or create User
        user, created = User.objects.get_or_create(
            email = email,
            defaults = {'is_verified': True}
        )
        if not user.is_verified:
            user.is_verified = True
            user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email,
            'is_new_user': created,
        }, status=status.HTTP_200_OK)