from django.contrib.auth import authenticate

from rest_framework import status

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import User

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

        return super().validate(attrs)