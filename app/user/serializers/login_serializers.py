from django.contrib.auth import authenticate

from rest_framework import status

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import User
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from user.models import EmailVerification

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    role = serializers.CharField(default='renter')
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        role = attrs.get("role", "renter")  # Default to renter if not specified

        # Create username from email and role
        username = f"{email}_{role}"
        
        user = authenticate(username=username, password=password)

        if not user:
            if not User.objects.filter(email=email, role=role).exists():
                raise serializers.ValidationError({
                    "email": f"User with this email and role doesn't exist"
                })  
            raise serializers.ValidationError({
                "password": "Invalid password"
            })        

        # Manually create the token data
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data['role'] = user.role
        data['email_verified'] = False
        if hasattr(user, 'email_verification'):
            data['email_verified'] = user.email_verification.is_verified

        data['name'] = None
        data['profile_image'] = None
        data['is_verified'] = None
        data['email'] = user.email
        data['id'] = user.id
        if user.role == 'merchant' and hasattr(user, 'merchantprofile'):
            data['name'] = user.merchantprofile.display_name
            data['is_verified'] = user.merchantprofile.is_verified
            if user.merchantprofile.profile_picture:
                data['profile_image'] = user.merchantprofile.profile_picture.url
        elif user.role == 'renter' and hasattr(user, 'renterprofile'):
            data['name'] = user.renterprofile.display_name
            if user.renterprofile.profile_picture:
                data['profile_image'] = user.renterprofile.profile_picture.url

        # Send verification code
        if not data['email_verified']:
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
            # send_mail(
            #     'Your Verification Code',
            #     f'Your verification code is: {code}',
            #     'noreply@niwebsolutions.agency',
            #     [email],
            #     fail_silently=False,
            # )
            # print(f"✅ Email sent successfully to {email}")

        return data