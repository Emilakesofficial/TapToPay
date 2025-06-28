from django.db import models
from django.conf import settings


class MerchantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='merchant_profile')
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tip_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    
    def __str__(self):
        return f"{self.user.username}'s Merchant Profile"
    
