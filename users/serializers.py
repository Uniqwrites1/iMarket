from rest_framework import serializers
from .models import User, OTPVerification
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password2', 'first_name',
            'last_name', 'profile_picture', 'phone_number', 'latitude', 'longitude',
            'is_verified', 'role'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'profile_picture', 'phone_number', 'latitude', 'longitude',
            'is_verified', 'date_joined', 'role'
        ]


class SellerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password2', 'first_name',
            'last_name', 'profile_picture', 'phone_number', 'latitude', 'longitude',
            'business_name', 'business_description'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'business_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        # Set role to seller
        validated_data['role'] = User.ROLE_SELLER
        user = User.objects.create_user(**validated_data)
        return user


class SellerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'profile_picture', 'phone_number', 'latitude', 'longitude',
            'is_verified', 'date_joined', 'business_name', 'business_description',
            'verification_status'
        ]


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for requesting OTP via email or phone"""
    email = serializers.EmailField(required=False)
    phone_number = PhoneNumberField(required=False)
    verification_type = serializers.ChoiceField(
        choices=[
            OTPVerification.TYPE_EMAIL, 
            OTPVerification.TYPE_PHONE,
            OTPVerification.TYPE_PASSWORD_RESET,
            OTPVerification.TYPE_LOGIN
        ]
    )
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        
        if not email and not phone_number:
            raise serializers.ValidationError(
                {"error": "Either email or phone_number must be provided"}
            )
            
        if attrs['verification_type'] == OTPVerification.TYPE_EMAIL and not email:
            raise serializers.ValidationError(
                {"email": "Email is required for email verification"}
            )
            
        if attrs['verification_type'] == OTPVerification.TYPE_PHONE and not phone_number:
            raise serializers.ValidationError(
                {"phone_number": "Phone number is required for phone verification"}
            )
            
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for verifying OTP codes"""
    email = serializers.EmailField(required=False)
    phone_number = PhoneNumberField(required=False)
    otp_code = serializers.CharField(required=True)
    verification_type = serializers.ChoiceField(
        choices=[
            OTPVerification.TYPE_EMAIL, 
            OTPVerification.TYPE_PHONE,
            OTPVerification.TYPE_PASSWORD_RESET,
            OTPVerification.TYPE_LOGIN
        ]
    )
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        
        if not email and not phone_number:
            raise serializers.ValidationError(
                {"error": "Either email or phone_number must be provided"}
            )
            
        if attrs['verification_type'] == OTPVerification.TYPE_EMAIL and not email:
            raise serializers.ValidationError(
                {"email": "Email is required for email verification"}
            )
            
        if attrs['verification_type'] == OTPVerification.TYPE_PHONE and not phone_number:
            raise serializers.ValidationError(
                {"phone_number": "Phone number is required for phone verification"}
            )
            
        return attrs


class EmailLoginSerializer(serializers.Serializer):
    """Serializer for email-based login (first step)"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")
        return value


class PhoneLoginSerializer(serializers.Serializer):
    """Serializer for phone-based login (first step)"""
    phone_number = PhoneNumberField(required=True)
    
    def validate_phone_number(self, value):
        try:
            User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this phone number")
        return value


class OTPLoginSerializer(serializers.Serializer):
    """Serializer for completing login with OTP"""
    email = serializers.EmailField(required=False)
    phone_number = PhoneNumberField(required=False)
    otp_code = serializers.CharField(required=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        
        if not email and not phone_number:
            raise serializers.ValidationError(
                {"error": "Either email or phone_number must be provided"}
            )
            
        return attrs

