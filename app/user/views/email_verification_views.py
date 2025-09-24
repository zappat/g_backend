from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from user.models import EmailVerification
from user.serializers import EmailVerificationVerifySerializer, EmailVerificationResendSerializer
from django.core.mail import send_mail
import random
from datetime import timedelta
from rest_framework.permissions import AllowAny

User = get_user_model()

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        try:
            users = User.objects.filter(email=email)
            if not users.exists():
                return Response({'message': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to find a user with a valid verification code
            ev = None
            for user in users:
                try:
                    ev = EmailVerification.objects.get(user=user)
                    if ev.code == code and not ev.is_verified and ev.expires_at > timezone.now():
                        break
                except EmailVerification.DoesNotExist:
                    continue
            
            if ev is None:
                return Response({'message': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
                
            user = ev.user
        except Exception:
            return Response({'message': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
        if ev.is_verified:
            return Response({'message': 'Email already verified.'}, status=status.HTTP_400_BAD_REQUEST)
        if ev.code != code:
            return Response({'message': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
        if ev.expires_at < timezone.now():
            return Response({'message': 'Verification code expired.'}, status=status.HTTP_400_BAD_REQUEST)
        ev.is_verified = True
        ev.save()
        return Response({'message': 'Email verified successfully.', 'role': user.role}, status=status.HTTP_200_OK)

class ResendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            users = User.objects.filter(email=email)
            if not users.exists():
                return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # If multiple users exist, we need to handle this case
            # For now, we'll send verification codes to all users with this email
            # In a real-world scenario, you might want to ask for role clarification
            for user in users:
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
        except Exception:
            return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # send_mail(
        #     'Your Verification Code',
        #     f'Your verification code is: {code}',
        #     'noreply@yourdomain.com',
        #     [email],
        #     fail_silently=False,
        # )
        return Response({'detail': 'Verification code resent.'}, status=status.HTTP_200_OK) 