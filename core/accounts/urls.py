from django.urls import path
from .views import RequestOTPView, VerifyOTPView
from rest_framework_simplejwt.views import TokenRefreshView
# from django.views.generic import TemplateView

app_name = "accounts"
urlpatterns = [
    path('otp/request/', RequestOTPView.as_view(), name='otp-request'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp-verify'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    # path('', TemplateView.as_view(template_name= "index.html"))
]