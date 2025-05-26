#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iMarket.settings')
django.setup()

from users.models import User
from django.contrib.auth import authenticate

print("=== Checking Users and Authentication ===")

# List all users
users = User.objects.all()
print(f"\nTotal users: {users.count()}")

for user in users:
    print(f"\nUser: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - Role: {user.role}")
    print(f"  - Is Active: {user.is_active}")
    print(f"  - Is Verified: {user.is_verified}")
    print(f"  - Has usable password: {user.has_usable_password()}")

# Test authentication with common passwords
test_passwords = ['testpass123', 'password123', 'admin123', 'seller123', 'buyer123']

print("\n=== Testing Authentication ===")

for user in users:
    print(f"\nTesting user: {user.username}")
    for password in test_passwords:
        auth_user = authenticate(username=user.username, password=password)
        if auth_user:
            print(f"  ✓ SUCCESS with password: {password}")
            break
    else:
        print(f"  ✗ FAILED with all test passwords")
        # Try to check password directly
        for password in test_passwords:
            if user.check_password(password):
                print(f"  ✓ Direct check SUCCESS with: {password}")
                break

# Reset passwords if needed
print("\n=== Resetting Passwords (if needed) ===")

try:
    buyer1 = User.objects.get(username='buyer1')
    buyer1.set_password('testpass123')
    buyer1.save()
    print("✓ Reset buyer1 password to 'testpass123'")
except User.DoesNotExist:
    print("✗ buyer1 user not found")

try:
    seller1 = User.objects.get(username='seller1')
    seller1.set_password('testpass123')
    seller1.save()
    print("✓ Reset seller1 password to 'testpass123'")
except User.DoesNotExist:
    print("✗ seller1 user not found")

print("\n=== Final Authentication Test ===")

# Test login again
buyer_auth = authenticate(username='buyer1', password='testpass123')
if buyer_auth:
    print("✓ buyer1 authentication SUCCESS")
else:
    print("✗ buyer1 authentication FAILED")

seller_auth = authenticate(username='seller1', password='testpass123')
if seller_auth:
    print("✓ seller1 authentication SUCCESS")
else:
    print("✗ seller1 authentication FAILED")
