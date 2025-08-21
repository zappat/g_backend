from rest_framework import generics, permissions
from .models import RFQ, RFQAttachment
from .serializers import RFQSerializer, RFQAttachmentSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from quote.models import Quote


class RFQListCreateView(generics.ListCreateAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Public can view only public RFQs; authenticated users see all
        base_qs = RFQ.objects.all()
        if not self.request.user.is_authenticated:
            base_qs = base_qs.filter(visibility='Public')
        return base_qs.order_by('-id')

    def get_permissions(self):
        # Allow unauthenticated read-only access; write requires authentication
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

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

    def get_queryset(self):
        # Restrict unauthenticated access to public RFQs only
        if not self.request.user.is_authenticated:
            return RFQ.objects.filter(visibility='Public')
        return RFQ.objects.all()

    def get_permissions(self):
        # Allow unauthenticated read-only access; write requires authentication
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


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

class RFQCloseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        try:
            rfq = RFQ.objects.get(id=pk)
            rfq.status = 'Closed'
            rfq.save()
            return Response({"id": rfq.id, "status": rfq.status}, status=status.HTTP_200_OK)
        except RFQ.DoesNotExist:
            return Response({"error": "RFQ not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        # Support POST as well
        return self.put(request, pk)
    
class RFQUpdateView(generics.UpdateAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Aggregate files from common keys used by frontends
            files = list(request.FILES.getlist('attachments')) + list(request.FILES.getlist('attachments[]'))

            # Detect explicit empty attachments intent: key present but no files
            has_attachments_key = ('attachments' in request.data) or ('attachments[]' in request.data)
            if has_attachments_key and not files:
                RFQAttachment.objects.filter(rfq=serializer.instance).delete()

            # If files are provided, replace all existing attachments with the new files
            if files:
                RFQAttachment.objects.filter(rfq=serializer.instance).delete()
                for file in files:
                    RFQAttachment.objects.create(rfq=serializer.instance, file=file)

            return Response(serializer.data)
        except Exception as e:
            print(f"RFQ Update error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RFQDeleteView(generics.DestroyAPIView):
    queryset = RFQ.objects.all()
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RFQQuoteCountView(APIView):
    """
    Returns the count of quotes for a specific RFQ
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            # Check if RFQ exists
            rfq = RFQ.objects.filter(pk=pk).first()
            if not rfq:
                return Response(
                    {"error": "RFQ not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Count quotes for this RFQ
            quote_count = Quote.objects.filter(rfq=pk).count()
            
            return Response({
                "rfq_id": pk,
                "quote_count": quote_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RFQIncrementViewsView(APIView):
    """
    Increments the view count for a specific RFQ
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            # Check if RFQ exists and increment views atomically
            rfq = RFQ.objects.filter(pk=pk).first()
            if not rfq:
                return Response(
                    {"error": "RFQ not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Increment views count atomically using F expression
            from django.db.models import F
            RFQ.objects.filter(pk=pk).update(views=F('views') + 1)
            
            # Get updated RFQ to return current view count
            rfq.refresh_from_db()
            
            return Response({
                "rfq_id": pk,
                "views": rfq.views,
                "message": "View count incremented successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )