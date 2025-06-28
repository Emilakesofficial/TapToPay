# reports/models.py
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.conf import settings

User = get_user_model()

class TransactionReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)  # success, failed
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.payment_reference} - {self.status}"


class DailySalesReport(models.Model):
    date = models.DateField(unique=True)
    total_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=('0.00'))
    total_transactions = models.PositiveIntegerField(default=0)
    successful_transactions = models.PositiveIntegerField(default=0)
    failed_transactions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Report for {self.date}"

