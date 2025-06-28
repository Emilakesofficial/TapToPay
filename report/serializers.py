from rest_framework import serializers
from .models import *

class DailySalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySalesReport
        fields = '__all__'

class TransactionReportSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = TransactionReport
        fields = '__all__'
        read_only_fields = ['user_name', 'payment_reference', 'timestamp']
        
    def get_user_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'