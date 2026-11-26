from django.urls import path
from .views import PaymentRequestView, PaymentResultView

urlpatterns = [
    path('request/', PaymentRequestView.as_view(), name='payment-request'),
    path('result/', PaymentResultView.as_view(), name='payment-result')
    # The callback and result are managed by the package.
]