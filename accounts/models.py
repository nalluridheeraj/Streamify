import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

# Add your existing models below this line if you had any
# Then add the OTP model:

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        expiry = self.created_at + timezone.timedelta(minutes=5)
        return not self.is_used and timezone.now() < expiry

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))