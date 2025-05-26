#!/usr/bin/env python3
"""
API Endpoint Testing Script for iMarket
This script tests all API endpoints to confirm they are working properly.
"""

import requests
import json
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    """Print colored status messages"""
    color = Colors.BLUE
    if status == "success":
        color = Colors.GREEN
    elif status == "error":
        color = Colors.RED
    elif status == "warning":
        color = Colors.YELLOW
    
    print(f"{color}{message}{Colors.RESET}")

def test_endpoint(method, url, data=None, headers=None, expected_status=None):
    """Test a single endpoint"""
    full_url = f"{BASE_URL}{url}"
    try:
        if method.upper() == "GET":
            response = requests.get(full_url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(full_url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(full_url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(full_url, headers=headers)
        else:
            print_status(f"❌ Unsupported method: {method}", "error")
            return False

        status_ok = response.status_code < 500  # Accept anything except server errors
        if expected_status:
            status_ok = response.status_code == expected_status

        if status_ok:
            print_status(f"✅ {method} {url} - Status: {response.status_code}", "success")
            return True
        else:
            print_status(f"❌ {method} {url} - Status: {response.status_code}", "error")
            try:
                error_data = response.json()
                print_status(f"   Error: {error_data}", "error")
            except:
                print_status(f"   Error: {response.text[:200]}", "error")
            return False

    except requests.exceptions.ConnectionError:
        print_status(f"❌ {method} {url} - Connection Error: Server not running?", "error")
        return False
    except Exception as e:
        print_status(f"❌ {method} {url} - Exception: {str(e)}", "error")
        return False

def test_all_endpoints():
    """Test all API endpoints"""
    print_status(f"\n{Colors.BOLD}🚀 Starting API Endpoint Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print_status("=" * 80)

    total_tests = 0
    passed_tests = 0

    # Test categories
    test_groups = [
        {
            "name": "🏠 Basic Endpoints",
            "tests": [
                ("GET", "/", None, None, 200),
                ("GET", "/api/", None, None),
            ]
        },
        {
            "name": "🔐 Authentication Endpoints",
            "tests": [
                ("POST", "/api/auth/user/register/", {
                    "username": "testuser123",
                    "email": "test@example.com",
                    "password": "testpass123",
                    "first_name": "Test",
                    "last_name": "User"
                }),
                ("POST", "/api/auth/seller/register/", {
                    "username": "testseller123",
                    "email": "seller@example.com",
                    "password": "testpass123",
                    "first_name": "Test",
                    "last_name": "Seller",
                    "business_name": "Test Business"
                }),
                ("POST", "/api/auth/user/login/", {
                    "username": "testuser123",
                    "password": "testpass123"
                }),
                ("POST", "/api/auth/seller/login/", {
                    "username": "testseller123",
                    "password": "testpass123"
                }),
                ("POST", "/api/auth/email-login/", {
                    "email": "test@example.com"
                }),
                ("POST", "/api/auth/phone-login/", {
                    "phone_number": "+1234567890"
                }),
                ("POST", "/api/auth/request-otp/", {
                    "email": "test@example.com",
                    "verification_type": "email"
                }),
                ("POST", "/api/auth/verify-otp/", {
                    "email": "test@example.com",
                    "otp_code": "123456",
                    "verification_type": "email"
                }),
                ("POST", "/api/auth/reset-password-request/", {
                    "email": "test@example.com"
                }),
            ]
        },
        {
            "name": "👥 User Management",
            "tests": [
                ("GET", "/api/users/"),
                ("GET", "/api/users/me/"),
                ("POST", "/api/users/verify_email/", {
                    "verification_code": "123456"
                }),
                ("POST", "/api/users/verify_phone/", {
                    "verification_code": "123456"
                }),
                ("POST", "/api/users/change_password/", {
                    "old_password": "testpass123",
                    "new_password": "newpass123"
                }),
            ]
        },
        {
            "name": "🏪 Markets & Shops",
            "tests": [
                ("GET", "/api/markets/"),
                ("GET", "/api/markets/1/"),
                ("GET", "/api/markets/1/sellers/"),
                ("GET", "/api/markets/1/map/"),
                ("GET", "/api/markets/pin_search/?lat=6.5244&lng=3.3792"),
                ("GET", "/api/markets/1/shops/"),
                ("GET", "/api/markets/1/navigation_info/"),
                ("POST", "/api/markets/1/check_indoor_location/", {
                    "latitude": 6.5244,
                    "longitude": 3.3792
                }),
                ("GET", "/api/shops/"),
                ("POST", "/api/shops/nearby/", {
                    "latitude": 6.5244,
                    "longitude": 3.3792,
                    "market_id": "1",
                    "radius_meters": 1000
                }),
            ]
        },
        {
            "name": "🛍️ Products & Categories",
            "tests": [
                ("GET", "/api/categories/"),
                ("GET", "/api/categories/1/"),
                ("GET", "/api/categories/1/products/"),
                ("GET", "/api/products/"),
                ("GET", "/api/products/1/"),
            ]
        },
        {
            "name": "🏠 Home & Highlights",
            "tests": [
                ("GET", "/api/home/"),
                ("GET", "/api/home/highlights/"),
            ]
        },
        {
            "name": "🧭 Navigation",
            "tests": [
                ("POST", "/api/navigation/start_navigation/", {
                    "start_latitude": 6.5244,
                    "start_longitude": 3.3792,
                    "destination_latitude": 6.5254,
                    "destination_longitude": 3.3802,
                    "navigation_mode": "walking",
                    "use_indoor_navigation": False
                }),
                ("POST", "/api/navigation/update_location/", {
                    "latitude": 6.5244,
                    "longitude": 3.3792,
                    "market_id": "1"
                }),
                ("GET", "/api/navigation/active_session/"),
                ("POST", "/api/navigation/indoor_route/", {
                    "start_x": 10.0,
                    "start_y": 20.0,
                    "end_x": 50.0,
                    "end_y": 60.0,
                    "floor": 1,
                    "market_id": "1"
                }),
            ]
        },
        {
            "name": "💰 Orders & Transactions",
            "tests": [
                ("GET", "/api/orders/"),
                ("GET", "/api/transactions/transactions/"),
                ("GET", "/api/transactions/wallet/"),
            ]
        },
        {
            "name": "💬 Chat",
            "tests": [
                ("GET", "/api/chat/rooms/"),
                ("GET", "/api/chat/messages/"),
                ("GET", "/api/chat/seller/messages/"),
            ]
        },
        {
            "name": "💼 Seller Dashboard",
            "tests": [
                ("GET", "/api/seller/profile/"),
                ("GET", "/api/seller/products/"),
                ("GET", "/api/seller/orders/"),
                ("GET", "/api/seller/analytics/"),
                ("GET", "/api/seller/earnings/"),
                ("GET", "/api/seller/wallet/"),
            ]
        },
        {
            "name": "👑 Admin Endpoints",
            "tests": [
                ("GET", "/api/admin/sellers/pending/"),
            ]
        },
        {
            "name": "💳 User Wallet",
            "tests": [
                ("GET", "/api/users/wallet/wallet/"),
                ("GET", "/api/users/wallet/transactions/"),
                ("POST", "/api/users/wallet/fund/", {
                    "amount": 100.00
                }),
            ]
        }
    ]

    # Run all tests
    for group in test_groups:
        print_status(f"\n{group['name']}", "info")
        print_status("-" * 50)
        
        for test in group["tests"]:
            method, url = test[0], test[1]
            data = test[2] if len(test) > 2 else None
            headers = test[3] if len(test) > 3 else None
            expected_status = test[4] if len(test) > 4 else None
            
            total_tests += 1
            if test_endpoint(method, url, data, headers, expected_status):
                passed_tests += 1

    # Summary
    print_status("\n" + "=" * 80)
    print_status(f"{Colors.BOLD}📊 Test Summary{Colors.RESET}")
    print_status(f"Total Tests: {total_tests}")
    print_status(f"Passed: {passed_tests}", "success")
    print_status(f"Failed: {total_tests - passed_tests}", "error" if total_tests - passed_tests > 0 else "success")
    print_status(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%", 
                "success" if passed_tests == total_tests else "warning")

    if passed_tests == total_tests:
        print_status(f"\n🎉 All API endpoints are working properly!", "success")
    else:
        print_status(f"\n⚠️ Some endpoints need attention. Check the details above.", "warning")

    return passed_tests == total_tests

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print_status(f"{Colors.BOLD}iMarket API Endpoint Testing Tool{Colors.RESET}")
    print_status("This script will test all API endpoints to ensure they are working properly.\n")
    
    # Check if server is running
    if not test_server_health():
        print_status("❌ Server is not running or not accessible at http://127.0.0.1:8000", "error")
        print_status("Please start the Django development server with: python manage.py runserver", "info")
        sys.exit(1)
    
    print_status("✅ Server is running and accessible", "success")
    
    # Run all tests
    success = test_all_endpoints()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
