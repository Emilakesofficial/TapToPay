from rest_framework import serializers
from .models import *

class MerchantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = ['tax_percentage', 'service_fee', 'tip_percentage']