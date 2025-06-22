from .models import *
from rest_framework import serializers
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product','quantity']
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    tip = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    fee = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'subtotal', 'tip', 'tax', 'fee','total' ]
        
    def get_subtotal(self, obj):
        return obj.calculate_subtotal()
    
    def get_tip(self, obj):
        return obj.calculate_tip()
    
    def get_tax(self, obj):
        return obj.calculate_tax()
    
    def get_fee(self, obj):
        return obj.calculate_fee()
    def get_total(self, obj):
        return obj.calculate_total()
    