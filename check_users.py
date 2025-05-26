#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iMarket.settings')
django.setup()

from users.models import User

def main():
    print("=== Checking Users ===")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"  {user.username} ({user.role}) - active: {user.is_active}")
        if user.username == 'buyer1':
            print(f"    Email: {user.email}")
            print(f"    Password check: {user.check_password('testpass123')}")
    
    # Check if buyer1 exists
    buyer1 = User.objects.filter(username='buyer1').first()
    if buyer1:
        print(f"\nBuyer1 found:")
        print(f"  Username: {buyer1.username}")
        print(f"  Role: {buyer1.role}")
        print(f"  Is active: {buyer1.is_active}")
        print(f"  Is verified: {buyer1.is_verified}")
        print(f"  Password check: {buyer1.check_password('testpass123')}")
    else:
        print("\nBuyer1 not found!")

if __name__ == '__main__':
    main()
