from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
import datetime
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    # Role choices
    ROLE_USER = 'user'
    ROLE_SELLER = 'seller'
    ROLE_ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (ROLE_USER, 'User/Buyer'),
        (ROLE_SELLER, 'Seller'),
        (ROLE_ADMIN, 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    # Replace CharField with PhoneNumberField for proper validation
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Role field
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    
    # Additional metadata
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Seller specific fields
    business_name = models.CharField(max_length=100, null=True, blank=True)
    business_description = models.TextField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        null=True,
        blank=True
    )
    verification_documents = models.JSONField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username
        
    def is_buyer(self):
        return self.role == self.ROLE_USER
        
    def is_seller(self):
        return self.role == self.ROLE_SELLER
        
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

class OTPVerification(models.Model):
    """Model to store OTP codes for email and phone verification"""
    TYPE_EMAIL = 'email'
    TYPE_PHONE = 'phone'
    TYPE_PASSWORD_RESET = 'password_reset'
    TYPE_LOGIN = 'login'
    
    TYPE_CHOICES = [
        (TYPE_EMAIL, 'Email Verification'),
        (TYPE_PHONE, 'Phone Verification'),
        (TYPE_PASSWORD_RESET, 'Password Reset'),
        (TYPE_LOGIN, 'Login Authentication'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    otp_code = models.CharField(max_length=6)
    verification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    
    def __str__(self):
        if self.user:
            return f"OTP for {self.user.username} - {self.verification_type}"
        elif self.email:
            return f"OTP for {self.email} - {self.verification_type}"
        elif self.phone_number:
            return f"OTP for {self.phone_number} - {self.verification_type}"
        return f"OTP - {self.verification_type}"
    
    def save(self, *args, **kwargs):
        # Set expiration time (10 minutes from creation)
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def increment_attempts(self):
        self.attempts += 1
        self.save()
