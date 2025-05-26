"""
Utility functions for handling OTP code generation, email, and SMS sending
"""
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Generate a numeric OTP code of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def send_email_otp(email, otp_code, verification_type):
    """Send OTP code via email"""
    subject_mapping = {
        'email': 'Email Verification for iMarket',
        'phone': 'Phone Verification for iMarket',
        'password_reset': 'Password Reset for iMarket',
        'login': 'Login Verification for iMarket',
    }
    
    message_mapping = {
        'email': f'Your email verification code is: {otp_code}. This code will expire in 10 minutes.',
        'phone': f'Your phone verification code is: {otp_code}. This code will expire in 10 minutes.',
        'password_reset': f'Your password reset code is: {otp_code}. This code will expire in 10 minutes.',
        'login': f'Your login verification code is: {otp_code}. This code will expire in 10 minutes.',
    }
    
    subject = subject_mapping.get(verification_type, 'Verification Code for iMarket')
    message = message_mapping.get(verification_type, f'Your verification code is: {otp_code}. This code will expire in 10 minutes.')
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False

def send_phone_otp(phone_number, otp_code):
    """Send OTP code via SMS using Twilio"""
    try:
        # Check if Twilio credentials are configured
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            logger.warning(f"Twilio credentials not configured. SMS to {phone_number} would contain: {otp_code}")
            # For development, return True but log the OTP
            if settings.DEBUG:
                print(f"[DEV MODE] SMS OTP for {phone_number}: {otp_code}")
                return True
            else:
                logger.error("Twilio credentials not configured for production")
                return False
        
        # Initialize the Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Send the SMS
        message = client.messages.create(
            body=f"Your iMarket verification code is: {otp_code}. This code will expire in 10 minutes.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(phone_number)
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False
