from django.core.mail import send_mail
from django.conf import settings
from .models import OTP

def send_otp(user):
    # Invalidate old OTPs
    OTP.objects.filter(user=user, is_used=False).update(is_used=True)

    code = OTP.generate_code()
    OTP.objects.create(user=user, code=code)

    send_mail(
        subject='Your OTP Code',
        message=f'Your OTP code is: {code}\n\nThis code expires in 5 minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    return code