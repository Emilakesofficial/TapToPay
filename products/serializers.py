from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class CustomUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUnit
        fields = ['id', 'unit']

class ProductSerializer(serializers.ModelSerializer):
    unit = CustomUnitSerializer(read_only=True)  # This just represents the unit object
    unit_id = serializers.PrimaryKeyRelatedField(queryset=CustomUnit.objects.all(), write_only=True)  # This expects the unit ID
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'unit', 'unit_id', 'price_per_unit', 'image','stock', 'is_available', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Pop unit_id from the validated_data and use it to create the Product
        unit = validated_data.pop('unit_id')
        product = Product.objects.create(unit=unit, **validated_data)
        product.update_availability() # Ensure availability is synced
        return product
    
    def update(self, instance, validated_data):
        # handle availability on update
        instance = super().update(instance, validated_data)
        instance.update_availability()
        return instance

