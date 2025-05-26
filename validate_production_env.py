#!/usr/bin/env python
"""
Production Environment Validation Script for iMarket Django Backend
Run this script to validate all required environment variables are properly set.
"""

import os
import sys
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file"""
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ .env file found and loaded")
        return True
    else:
        print("❌ .env file not found")
        print("💡 Create .env file from .env.production.template")
        return False

def validate_required_vars():
    """Validate all required environment variables"""
    
    print("\n🔍 Validating Required Environment Variables")
    print("=" * 60)
    
    # Define required variables with their descriptions
    required_vars = {
        # Core Django
        'DJANGO_SECRET_KEY': 'Django secret key for cryptographic signing',
        'DJANGO_DEBUG': 'Debug mode (should be False for production)',
        'DJANGO_ALLOWED_HOSTS': 'Allowed host names for the application',
        
        # Database
        'DB_NAME': 'Database name',
        'DB_USER': 'Database username', 
        'DB_PASSWORD': 'Database password',
        'DB_HOST': 'Database host',
        'DB_PORT': 'Database port',
        
        # Email (Required for OTP)
        'EMAIL_HOST_USER': 'Email username for SMTP',
        'EMAIL_HOST_PASSWORD': 'Email password for SMTP',
        'DEFAULT_FROM_EMAIL': 'Default from email address',
    }
    
    # Optional but recommended variables
    optional_vars = {
        # SMS/Twilio
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID for SMS',
        'TWILIO_AUTH_TOKEN': 'Twilio Auth Token for SMS',
        'TWILIO_PHONE_NUMBER': 'Twilio phone number for SMS',
        
        # Mapping APIs
        'GOOGLE_MAPS_API_KEY': 'Google Maps API key for navigation',
        'MAPBOX_ACCESS_TOKEN': 'Mapbox access token for maps',
        
        # Redis (for production WebSockets)
        'REDIS_HOST': 'Redis host for WebSocket channels',
        'REDIS_PORT': 'Redis port for WebSocket channels',
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required variables
    print("\n📋 Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if any(sensitive in var.lower() for sensitive in ['password', 'key', 'token', 'secret']):
                display_value = '*' * len(value) if len(value) > 0 else 'EMPTY'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET - {description}")
            missing_required.append(var)
    
    # Check optional variables
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if any(sensitive in var.lower() for sensitive in ['password', 'key', 'token', 'secret']):
                display_value = '*' * len(value) if len(value) > 0 else 'EMPTY'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: NOT SET - {description}")
            missing_optional.append(var)
    
    return missing_required, missing_optional

def validate_specific_settings():
    """Validate specific settings values"""
    
    print("\n🔧 Validating Specific Settings:")
    print("=" * 40)
    
    issues = []
    
    # Check DEBUG setting
    debug = os.getenv('DJANGO_DEBUG', 'True')
    if debug.lower() == 'true':
        print("⚠️  DJANGO_DEBUG is True - Should be False for production")
        issues.append("Set DJANGO_DEBUG=False for production")
    else:
        print("✅ DJANGO_DEBUG is properly set to False")
    
    # Check SECRET_KEY
    secret_key = os.getenv('DJANGO_SECRET_KEY', '')
    if secret_key == 'your-default-secret-key' or len(secret_key) < 50:
        print("❌ DJANGO_SECRET_KEY is default or too short")
        issues.append("Generate a strong secret key (50+ characters)")
    else:
        print("✅ DJANGO_SECRET_KEY appears to be properly set")
    
    # Check ALLOWED_HOSTS
    allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '')
    if not allowed_hosts or allowed_hosts == '':
        print("❌ DJANGO_ALLOWED_HOSTS is empty")
        issues.append("Set DJANGO_ALLOWED_HOSTS to your domain names")
    else:
        print(f"✅ DJANGO_ALLOWED_HOSTS: {allowed_hosts}")
    
    # Check email configuration
    email_user = os.getenv('EMAIL_HOST_USER', '')
    email_pass = os.getenv('EMAIL_HOST_PASSWORD', '')
    if email_user and email_pass:
        print("✅ Email configuration appears complete")
    else:
        print("⚠️  Email configuration incomplete - OTP emails may not work")
        issues.append("Configure email settings for OTP functionality")
    
    return issues

def main():
    """Main validation function"""
    
    print("🚀 iMarket Production Environment Validation")
    print("=" * 50)
    
    # Load environment variables
    if not load_env():
        print("\n❌ Cannot proceed without .env file")
        sys.exit(1)
    
    # Validate required variables
    missing_required, missing_optional = validate_required_vars()
    
    # Validate specific settings
    issues = validate_specific_settings()
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 30)
    
    if missing_required:
        print(f"❌ Missing Required Variables: {len(missing_required)}")
        for var in missing_required:
            print(f"   - {var}")
    else:
        print("✅ All required variables are set")
    
    if missing_optional:
        print(f"⚠️  Missing Optional Variables: {len(missing_optional)}")
        for var in missing_optional:
            print(f"   - {var}")
    else:
        print("✅ All optional variables are set")
    
    if issues:
        print(f"\n⚠️  Configuration Issues: {len(issues)}")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No configuration issues found")
    
    # Final recommendation
    print("\n💡 Next Steps:")
    if missing_required or issues:
        print("1. Fix the required variables and issues listed above")
        print("2. Re-run this script to validate")
        print("3. Test the application thoroughly")
        sys.exit(1)
    else:
        print("1. Your environment appears ready for production")
        print("2. Run a full API test: python test_api_endpoints.py")
        print("3. Deploy with confidence! 🚀")

if __name__ == "__main__":
    main()
