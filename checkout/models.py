from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tip_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tip_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def calculate_subtotal(self):
        # Access items using 'items.all()' (because of related_name='items')
        return sum(Decimal(item.product.price_per_unit) * Decimal(item.quantity) for item in self.items.all())

    def calculate_tip(self):
        return Decimal(self.calculate_subtotal()) * Decimal(0.05)  # Example: 5% tip

    def calculate_tax(self):
        return Decimal(self.calculate_subtotal()) * Decimal(0.075)  # Example: 7.5% tax

    def calculate_fee(self):
        return Decimal(100)  # Example: flat service fee

    def calculate_total(self):
        return self.calculate_subtotal() + self.calculate_tip() + self.calculate_tax() + self.calculate_fee()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('cart', 'product')
    
       



