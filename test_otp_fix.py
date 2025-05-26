#!/usr/bin/env python
"""
Test script to verify OTP endpoint fix
"""
import requests
import json

def test_otp_email():
    """Test OTP request via email"""
    url = 'http://127.0.0.1:8000/api/auth/request-otp/'
    data = {
        'email': 'test@example.com',
        'verification_type': 'email'
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"✅ Email OTP Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Email OTP Error: {e}")
        return False

def test_otp_phone():
    """Test OTP request via phone"""
    url = 'http://127.0.0.1:8000/api/auth/request-otp/'
    data = {
        'phone_number': '+1234567890',
        'verification_type': 'phone'
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"✅ Phone OTP Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Phone OTP Error: {e}")
        return False

def main():
    print("🔧 Testing OTP Endpoint Fix")
    print("=" * 40)
    
    email_success = test_otp_email()
    print()
    phone_success = test_otp_phone()
    
    print("\n📊 Test Results:")
    print(f"Email OTP: {'✅ PASSED' if email_success else '❌ FAILED'}")
    print(f"Phone OTP: {'✅ PASSED' if phone_success else '❌ FAILED'}")
    
    if email_success and phone_success:
        print("\n🎉 All OTP endpoints are working correctly!")
    else:
        print("\n⚠️ Some OTP endpoints need attention.")

if __name__ == "__main__":
    main()
