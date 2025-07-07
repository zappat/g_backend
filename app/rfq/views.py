from rest_framework import generics, permissions
from .models import RFQ, RFQAttachment
from .serializers import RFQSerializer, RFQAttachmentSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

class RFQListCreateView(generics.ListCreateAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RFQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]

class RFQAttachmentUploadView(generics.CreateAPIView):
    queryset = RFQAttachment.objects.all()
    serializer_class = RFQAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 