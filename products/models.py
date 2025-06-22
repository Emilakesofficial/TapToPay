from django.db import models
from django.contrib.auth.models import User


class CustomUnit(models.Model):
    unit = models.CharField(max_length=20)
       
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 255)
    description = models.TextField()
    image = models.ImageField(upload_to='product_pics', blank=False, null=False)
    unit = models.ForeignKey(CustomUnit, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=30, default=0.00)
    quantity = models.PositiveBigIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def update_availability(self):
        self.is_available = self.quantity > 0
        self.save()
        
    def save(self, *args, **kwargs):
        self.is_available = self.quantity > 0
        super().save(*args, **kwargs)
        
    def __str__(self):
        return(self.name)
    
