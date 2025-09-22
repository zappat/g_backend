"""Views for the user APIs"""
from django.contrib.auth import get_user_model

from rest_framework import (generics, permissions, status)
from rest_framework.response import Response
from user.serializers import UserSerializer
from user.utils import get_tokens_for_user
from user.models import EmailVerification
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
import uuid
from django.db.models import Q

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        instance = super(CreateUserView, self).post(request, *args, **kwargs)
        email = instance.data.get('email')
        role = instance.data.get('role')
        # Get the specific user by email and role since we now allow same email for different roles
        user = get_user_model().objects.get(email=email, role=role)
        print(f"🔑 User created: {user}")
        token = get_tokens_for_user(user)

        # Send verification code
        code = f"{random.randint(100000, 999999)}"
        expires_at = timezone.now() + timedelta(minutes=10)
        ev, created = EmailVerification.objects.get_or_create(
            user=user,
            defaults={
                'code': code,
                'expires_at': expires_at,
                'is_verified': False,
            }
        )
        if not created:
            ev.code = code
            ev.expires_at = expires_at
            ev.is_verified = False
            ev.save()
        try:
            print(f"📧 Attempting to send verification email to: {email}")
            print(f"📧 Using SMTP settings: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            
            send_mail(
                'Your Verification Code',
                f'Your verification code is: {code}',
                'noreply@niwebsolutions.agency',
                [email],
                fail_silently=False,
            )
            print(f"✅ Email sent successfully to {email}")
            
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback:")
            traceback.print_exc()
            
            # Still return success to user, but log the email error
            print(f"⚠️  User registration successful, but email verification failed")

        return Response(token, status=status.HTTP_201_CREATED)



class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return authenticated user."""
        return self.request.user


class UserDeleteApiView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = get_user_model().objects.all()


class UpdateUserByEmailView(generics.UpdateAPIView):
    """Update a user by their email address"""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'email'
    queryset = get_user_model().objects.all()

    def update(self, request, *args, **kwargs):
        try:
            # Get the user instance
            instance = self.get_object()
            
            # Handle role update
            role = request.data.get('role')
            if role:
                # Validate role value
                if role not in ['merchant', 'renter']:
                    return Response(
                        {'error': 'Invalid role. Must be either "merchant" or "renter"'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update role directly
                instance.role = role
                instance.save()
            
            # Perform other updates if any
            other_data = {k: v for k, v in request.data.items() if k != 'role'}
            if other_data:
                serializer = self.get_serializer(instance, data=other_data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            else:
                serializer = self.get_serializer(instance)
            
            return Response(serializer.data)
            
        except get_user_model().DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
       