from rest_framework import generics, permissions
from .models import RFQ, RFQAttachment
from .serializers import RFQSerializer, RFQAttachmentSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class RFQListCreateView(generics.ListCreateAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        rfq = serializer.save(created_by=self.request.user)
        
        # Handle file attachments
        files = self.request.FILES.getlist('attachments')
        for file in files:
            RFQAttachment.objects.create(rfq=rfq, file=file)

    def create(self, request, *args, **kwargs):
        try:
            # Remove created_by from data if it exists (it's set automatically)
            data = request.data.copy()
            if 'created_by' in data:
                del data['created_by']

            print("data", data)
            
            serializer = self.get_serializer(data=data)

            print("serializer", serializer)
            if not serializer.is_valid():
                print("Validation errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Call perform_create directly instead of super().create()
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Exception occurred:", str(e))
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class RFQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]


class RFQSaveView(APIView):
    """Save/Unsave an RFQ"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, rfq_id):
        try:
            rfq = RFQ.objects.get(id=rfq_id)
            rfq.saved = not rfq.saved  # Toggle saved status
            rfq.save()
            
            return Response({
                'id': rfq.id,
                'saved': rfq.saved,
                'message': f"RFQ {'saved' if rfq.saved else 'unsaved'} successfully"
            }, status=status.HTTP_200_OK)
        except RFQ.DoesNotExist:
            return Response(
                {"error": "RFQ not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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