from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.functional import cached_property
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def _calculate_subtotal(self):
        return sum(
            Decimal(item.product.price_per_unit) * Decimal(item.quantity)
            for item in self.items.all()
        )

    @cached_property
    def subtotal(self):
        return round(self._calculate_subtotal(), 2)

    def calculate_tax(self):
        merchant = getattr(self.user, 'merchant_profile', None)
        if not merchant:
            return Decimal('0.00')
        return round((merchant.tax_percentage / 100) * self.subtotal, 2)

    def calculate_fee(self):
        merchant = getattr(self.user, 'merchant_profile', None)
        if not merchant:
            return Decimal('0.00')
        return round(merchant.service_fee, 2)

    def calculate_tip(self):
        merchant = getattr(self.user, 'merchant_profile', None)
        if not merchant:
            return Decimal('0.00')
        return round((merchant.tip_percentage / 100) * self.subtotal, 2)

    def calculate_total(self):
        return round(
            self.subtotal +
            self.calculate_tip() +
            self.calculate_tax() +
            self.calculate_fee(),
            2
        )

    def __str__(self):
        return f"{self.user.username}'s cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
