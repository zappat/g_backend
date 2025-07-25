from django.contrib.auth import authenticate

from rest_framework import status

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import User
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from user.models import EmailVerification

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    "email":"User with this email doesn't exist"
                })  
            raise serializers.ValidationError({
                "password": "Invalid password"
            })        

        data = super().validate(attrs)
        data['role'] = user.role
        data['is_verified'] = False
        if hasattr(user, 'email_verification'):
            data['is_verified'] = user.email_verification.is_verified

        # Send verification code
        if not data['is_verified']:
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
            send_mail(
                'Your Verification Code',
                f'Your verification code is: {code}',
                'noreply@yourdomain.com',
                [email],
                fail_silently=False,
            )

        return data