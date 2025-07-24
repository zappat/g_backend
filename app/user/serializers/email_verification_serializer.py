from rest_framework import serializers

class EmailVerificationVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class EmailVerificationResendSerializer(serializers.Serializer):
    email = serializers.EmailField() 