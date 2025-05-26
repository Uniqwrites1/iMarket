#!/usr/bin/env python
"""
Debug script to test OTP functionality and identify the exact issue
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iMarket.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from users.utils import send_email_otp, send_phone_otp, generate_otp

def test_email_configuration():
    """Test email configuration"""
    print("🔍 Testing Email Configuration")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()

def test_sms_configuration():
    """Test SMS configuration"""
    print("🔍 Testing SMS Configuration")
    print(f"TWILIO_ACCOUNT_SID: {'*' * len(settings.TWILIO_ACCOUNT_SID) if settings.TWILIO_ACCOUNT_SID else 'NOT SET'}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(settings.TWILIO_AUTH_TOKEN) if settings.TWILIO_AUTH_TOKEN else 'NOT SET'}")
    print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER if settings.TWILIO_PHONE_NUMBER else 'NOT SET'}")
    print()

def test_otp_generation():
    """Test OTP generation"""
    print("🔍 Testing OTP Generation")
    otp = generate_otp()
    print(f"Generated OTP: {otp}")
    print(f"OTP Length: {len(otp)}")
    print(f"OTP Type: {type(otp)}")
    print()

def test_email_sending():
    """Test email sending functionality"""
    print("🔍 Testing Email Sending")
    test_email = 'test@example.com'
    test_otp = generate_otp()
    
    try:
        result = send_email_otp(test_email, test_otp, 'email')
        print(f"Email sending result: {result}")
        if not result:
            print("❌ Email sending failed")
        else:
            print("✅ Email sending succeeded")
    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
    print()

def test_console_email_backend():
    """Test with console email backend for development"""
    print("🔍 Testing Console Email Backend")
    
    # Temporarily change email backend for testing
    original_backend = settings.EMAIL_BACKEND
    settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    try:
        result = send_mail(
            'Test Email',
            'This is a test email for OTP functionality',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False,
        )
        print(f"Console email test result: {result}")
        print("✅ Console email backend works")
    except Exception as e:
        print(f"❌ Console email backend error: {str(e)}")
    finally:
        # Restore original backend
        settings.EMAIL_BACKEND = original_backend
    print()

def main():
    print("🚀 OTP Debug Testing - Django iMarket")
    print("=" * 50)
    
    test_email_configuration()
    test_sms_configuration()
    test_otp_generation()
    test_email_sending()
    test_console_email_backend()
    
    print("💡 Recommendations:")
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("- Set up email credentials in environment variables or .env file")
        print("- For development, consider using console email backend")
    
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("- Set up Twilio credentials for SMS functionality")
        print("- For development, you can disable SMS and use email only")
    
    print("\n🔧 Quick Fix for Development:")
    print("Add this to your settings.py for development email testing:")
    print("EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")

if __name__ == "__main__":
    main()
