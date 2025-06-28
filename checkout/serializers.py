from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializers import ProductSerializer  

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    tip = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    service_fee = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'created_at',
            'items', 'subtotal', 'tip', 'tax', 'service_fee', 'total'
        ]
        read_only_fields = ['user', 'created_at', 'subtotal', 'tip', 'tax', 'service_fee', 'total']
        

    def get_subtotal(self, obj):
        return obj.subtotal

    def get_tip(self, obj):
        return obj.calculate_tip()

    def get_tax(self, obj):
        return obj.calculate_tax()

    def get_service_fee(self, obj):
        return obj.calculate_fee()

    def get_total(self, obj):
        return obj.calculate_total()
