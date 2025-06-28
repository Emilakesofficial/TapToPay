from rest_framework import serializers
from .models import *

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'cart', 'amount', 'reference', 'verified', 'created_at', 'status']
        read_only_fields = ['id', 'verified','created_at', 'user', 'status']
        