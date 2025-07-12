"""
Utility functions for handling OTP code generation and email sending
"""
import random
import string
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Generate a numeric OTP code of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def send_email_otp(email, otp_code, verification_type):
    """Send OTP code via email"""
    subject_mapping = {
        'email': 'Email Verification for iMarket',
        'phone': 'Phone Verification for iMarket (via Email)',
        'password_reset': 'Password Reset for iMarket',
        'login': 'Login Verification for iMarket',
    }
    
    message_mapping = {
        'email': f'Your email verification code is: {otp_code}. This code will expire in 10 minutes.',
        'phone': f'Your phone verification code is: {otp_code}. This code will expire in 10 minutes. (Sent via email as SMS is not available)',
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
    """Phone OTP is not available - using email fallback"""
    logger.warning(f"SMS OTP not available. Phone verification for {phone_number} disabled.")
    return False
