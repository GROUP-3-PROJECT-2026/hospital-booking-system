"""
Development Authentication Backend
Automatically authenticates any user for development purposes.
This bypasses the need for creating user accounts during development.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


class DevelopmentAuthBackend(BaseBackend):
    """
    Authentication backend that automatically logs in any user.
    Use only for development/testing purposes.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Always return a user object without validating credentials.
        This allows any username/password combination to work.
        """
        if username and password:
            # Try to get or create the user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user with the provided username
                user = User.objects.create_user(
                    username=username,
                    password=password or 'dev123',  # Default password for new users
                    is_staff=True,
                    is_superuser=True
                )
                print(f"Created new user: {username}")
            
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None