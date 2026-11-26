from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(email, code):
    """
    Send OTP verification emial.
    Configure EMAIL_* settings in settings.py for production
    """
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}\n\nThis code expires in 10 minutes.'

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )