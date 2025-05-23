from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.serializers import AdditionalEmailSerializer, AdditionalPhoneNumberSerializer, AdditionalInfoSerializer
from user.models import AdditionalEmail, AdditionalPhoneNumber
from user.permissions import IsProvider

class AdditionalPhoneNumberCreateAPIView(generics.CreateAPIView):
    """Create a new additional phone number associated to user."""
    permission_classes = (IsAuthenticated, IsProvider)
    queryset = AdditionalPhoneNumber.objects.all()
    serializer_class = AdditionalPhoneNumberSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdditionalEmailCreateAPIView(generics.CreateAPIView):
    """Create a new additional email associated to user."""
    permission_classes = (IsAuthenticated, IsProvider)
    queryset = AdditionalEmail.objects.all()
    serializer_class = AdditionalEmailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdditionalEmailUpdateAPIView(generics.UpdateAPIView):
    """Update additional email associated to user."""
    permission_classes = (IsAuthenticated, IsProvider)
    queryset = AdditionalEmail.objects.all()
    serializer_class = AdditionalEmailSerializer

    def get_object(self):
        user = self.request.user
        additional_email_id = self.kwargs.get("id")
        return get_object_or_404(AdditionalEmail, id=additional_email_id, user=user)


class AdditionalPhoneNumberUpdateAPIView(generics.UpdateAPIView):
    """Update additional phone number associated to user."""
    permission_classes = (IsAuthenticated, IsProvider)
    queryset = AdditionalPhoneNumber.objects.all()
    serializer_class = AdditionalPhoneNumberSerializer

    def get_object(self):
        user = self.request.user
        additional_phone_number_id = self.kwargs.get("id")
        return get_object_or_404(AdditionalPhoneNumber, id=additional_phone_number_id, user=user)


class AdditionalInfoRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieves the additional info number associated to user."""
    permission_classes = (IsAuthenticated, IsProvider)
    queryset = AdditionalEmail.objects.all()
    serializer_class = AdditionalInfoSerializer

    def get_object(self):
        user = self.request.user
        return {
            "additional_phone_number": AdditionalPhoneNumber.objects.filter(user=user),
            "additional_email": AdditionalEmail.objects.filter(user=user),
        }
