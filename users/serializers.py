from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',]

    def to_internal_value(self, data): # is a DRF serializer class method that allows us to customize our validation
        allowed_fields = set(self.fields.keys())
        received_fields = set(data.keys())

        disallowed_fields = received_fields - allowed_fields
        if disallowed_fields:
            raise serializers.ValidationError(
                {field: "You are not allowed to update this field." for field in disallowed_fields}
            )

        return super().to_internal_value(data)

        
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    country = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Profile
        fields = ['user','business_name', 'country', 'image']
    
    def get_country(self, obj):
        return obj.country.name if obj.country else None
    # extract user data
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # update first and last name only
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.save()
        
        #update profile field
        for data, value in validated_data.items():
            setattr(instance, data, value)
        instance.save()

        return instance
        
class RegisterSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(write_only=True)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'business_name', 'country', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match')

        if len(password) < 8:
            raise serializers.ValidationError({"Password": "Password must be at least 8 characters long"})

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError('Password must contain at least one number')

        if not any(char.isupper() for char in password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')

        special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/~`"
        if not any(char in special_characters for char in password):
            raise serializers.ValidationError('Password must contain at least one special character')

        return data

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already taken.")
        return email

    def validate_business_name(self, value):
        if Profile.objects.filter(business_name=value).exists():
            raise serializers.ValidationError("This business name is already taken.")
        return value

    def create(self, validated_data):
        email = validated_data['email'].lower() # Username = email
        validated_data['email'] = email
        validated_data['username'] = email
        
        business_name = validated_data.pop('business_name')
        country = validated_data.pop('country')
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        Profile.objects.create(user=user, business_name=business_name, country=country)
        return user
    
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code','currency_code', 'currency_symbol']
        
class VerifyOldPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required = True)
    
    def validate_old_password(self, data):
        user = self.context['request'].user
        if not user.check_password(data):
            raise serializers.ValidationError('Old password incorrect')
        return data
    
class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    
    def validate(self, data):
        user = self.context['request'].user
        otp = data.get('otp')
        
        try:
            otp_obj = PasswordOTP.objects.get(user=user)
        except PasswordOTP.DoesNotExist:
            raise serializers.ValidationError({'code':'No OTP found, request a new one.'})
        
        if not otp_obj.is_valid(otp):
            raise serializers.ValidationError({"code": "Invalid or expired OTP."})
        
        # delete otp after use
        otp_obj.delete()
        return data
    
class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError('passwords does not match')
        
        if len(new_password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})

        if not any(char.isdigit() for char in new_password):
            raise serializers.ValidationError('Password must contain at least one number')

        if not any(char.isupper() for char in new_password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')
        
        if not any(char.islower() for char in new_password):
            raise serializers.ValidationError('Password must contain at least one lowercase letter')
        
        special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/~`"
        if not any(char in special_characters for char in new_password):
            raise serializers.ValidationError('Password must contain at least one special character')
        return data 

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    def validate(self, data):
        new_password = data.get('new_password')
        if len(new_password) < 8:
                raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})

        if not any(char.isdigit() for char in new_password):
            raise serializers.ValidationError('Password must contain at least one number')

        if not any(char.isupper() for char in new_password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')
        
        if not any(char.islower() for char in new_password):
            raise serializers.ValidationError('Password must contain at least one lowercase letter')
        
        special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/~`"
        if not any(char in special_characters for char in new_password):
            raise serializers.ValidationError('Password must contain at least one special character')
        return data 

        
    
