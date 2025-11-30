#!/usr/bin/env python
"""
Comprehensive script to fix login issue by creating admin user and testing authentication.
Run this in your Django project directory.
"""

import os
import sys
import django

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

def test_authentication(username, password):
    """Test if authentication works"""
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            print(f"✅ Authentication test PASSED for user: {username}")
            return True
        else:
            print(f"❌ Authentication test FAILED for user: {username}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def fix_admin_login():
    """Fix admin login by creating a known working user"""
    
    username = 'admin'
    password = 'admin123'
    email = 'admin@hospital.com'
    
    print("🔧 Fixing admin login...")
    
    # List existing users
    print(f"\n📋 Current users in database:")
    for user in User.objects.all():
        print(f"   - {user.username} (Active: {user.is_active}, Staff: {user.is_staff})")
    
    # Delete existing admin if any
    try:
        admin_user = User.objects.get(username=username)
        admin_user.delete()
        print(f"✅ Deleted existing user: {username}")
    except User.DoesNotExist:
        print(f"ℹ️  No existing user: {username}")
    
    # Create new admin user
    try:
        admin_user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            first_name='Admin',
            last_name='User'
        )
        
        print("🎉 SUCCESS! Admin user created:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        
        # Verify user exists and test authentication
        verify_user = User.objects.get(username=username)
        print(f"\n🔍 User verification:")
        print(f"   - Exists: ✅")
        print(f"   - Active: {verify_user.is_active}")
        print(f"   - Staff: {verify_user.is_staff}")
        print(f"   - Superuser: {verify_user.is_superuser}")
        
        # Test authentication
        print(f"\n🧪 Testing authentication...")
        auth_success = test_authentication(username, password)
        
        if auth_success:
            print("\n✅ All tests PASSED! Login should work now.")
            return True
        else:
            print("\n⚠️  User created but authentication failed. Check password hashing.")
            return False
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 Hospital Booking System - Comprehensive Login Fix")
    print("=" * 60)
    
    success = fix_admin_login()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ FIX COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🌐 Try logging in at: http://127.0.0.1:8000/accounts/login/")
        print("👤 Username: admin")
        print("🔑 Password: admin123")
        print("\n💡 If login still fails, there may be session/CSRF issues.")
        print("   Try clearing browser cache and cookies.")
    else:
        print("\n" + "=" * 60)
        print("❌ FIX FAILED")
        print("=" * 60)
        print("Please check the error messages above.")