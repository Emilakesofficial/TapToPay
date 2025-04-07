from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
import re

class RegisterSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email', 'business_name','country', 'password', 'confirm_password']
        extra_kwargs ={
            'password': {'write_only':True},
            'confirm_password':{'write_only':True}
        }
        
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match')

        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError('Password must contain at least one number')

        if not any(char.isupper() for char in password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')
        
        special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/~`"
        if not any(char in special_characters for char in password):
            raise serializers.ValidationError('Password must contain at least one special character')

        return data

        

    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        country = validated_data.pop('country')
        validated_data.pop('confirm_password')
        
        user = User.objects.create_user(**validated_data)
        profile = Profile.objects.create(user=user)
        profile.business_name = business_name
        profile.country = country
        profile.save()

        return user