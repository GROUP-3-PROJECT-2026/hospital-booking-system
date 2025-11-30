#!/usr/bin/env python
"""
Script to create a default admin user for the hospital booking system.
Run this script to create a admin user with known credentials.
"""

import os
import django
import sys

# Setup Django
sys.path.append('/c/Users/ADMIN/OneDrive/Desktop/Hospital booking system/hospital-booking-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def create_admin_user():
    """Create or update admin user with known credentials"""
    username = 'admin'
    email = 'admin@hospital.com'
    password = 'admin123'  # Simple password without special chars
    
    # Delete existing admin user if exists
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"Deleted existing user: {username}")
    except User.DoesNotExist:
        pass
    
    # Create new admin user
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    
    print(f"Created admin user successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    
    return user

if __name__ == '__main__':
    try:
        create_admin_user()
        print("\n✅ Admin user created successfully!")
        print("You can now login with:")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print("Please run this script from the hospital-booking-system directory")