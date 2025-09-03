from rest_framework import generics, permissions
from .models import RFQ, RFQAttachment
from .serializers import RFQSerializer, RFQAttachmentSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import QueryDict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from quote.models import Quote
from core.models import User
from django.shortcuts import get_object_or_404
from django.db import models


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


class RFQSavedView(APIView):
    """
    Save or unsave an RFQ for a user.
    POST /api/rfq/rfqs/save/
    Body: { "rfq_id": 123, "user": "user@example.com" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("DEBUG: RFQSavedView.post called")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request content type: {request.content_type}")

        try:
            # Handle different content types - be careful about accessing request.data vs request.body
            if 'text/plain' in request.content_type:
                # Parse JSON from text/plain request - read body directly
                import json
                print(f"DEBUG: Request body: {request.body}")
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    print("DEBUG: Parsed data from body:", data)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid JSON in request body"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif request.content_type == 'application/json':
                # Use request.data for JSON requests
                print(f"DEBUG: Request data: {request.data}")
                data = request.data
            else:
                # For other content types, try request.data but don't access body
                print("DEBUG: Using request.data for other content types")
                data = request.data

            # Extract data from request
            rfq_id = data.get('rfq_id')
            user_email = data.get('user')
            print("DEBUG: rfq_id:", rfq_id)
            print("DEBUG: user_email:", user_email)

            if not rfq_id or not user_email:
                return Response(
                    {"error": "Both 'rfq_id' and 'user' are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the user
            print("DEBUG: Looking up user with email:", user_email)
            try:
                user = User.objects.get(email=user_email)
                print("DEBUG: User found:", user.id, user.email)
            except User.DoesNotExist:
                print("DEBUG: User not found with email:", user_email)
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the RFQ
            print("DEBUG: Looking up RFQ with id:", rfq_id)
            try:
                rfq = RFQ.objects.get(id=rfq_id)
                print("DEBUG: RFQ found:", rfq.id, rfq.title)
            except RFQ.DoesNotExist:
                print("DEBUG: RFQ not found with id:", rfq_id)
                return Response(
                    {"error": "RFQ not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if user already saved this RFQ
            print("DEBUG: Checking if user already saved this RFQ")
            is_saved = rfq.saved_by.filter(id=user.id).exists()
            print("DEBUG: is_saved:", is_saved)

            if is_saved:
                # Unsave the RFQ
                print("DEBUG: Unsaving RFQ")
                rfq.saved_by.remove(user)
                action = "unsaved"
                message = f"RFQ {rfq_id} unsaved successfully"
                print("DEBUG: RFQ unsaved successfully")
            else:
                # Save the RFQ
                print("DEBUG: Saving RFQ")
                rfq.saved_by.add(user)
                action = "saved"
                message = f"RFQ {rfq_id} saved successfully"
                print("DEBUG: RFQ saved successfully")

            return Response({
                "rfq_id": rfq_id,
                "user": user_email,
                "action": action,
                "message": message,
                "saved_count": rfq.saved_by.count()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RFQByUserView(generics.ListAPIView):
    """
    Get RFQs created by a specific user.
    GET /api/rfq/rfqs/get-by-user/<user_id>/
    """
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')

        if not user_id:
            return RFQ.objects.none()

        # Filter RFQs by created_by user ID
        queryset = RFQ.objects.filter(created_by_id=user_id)

        # Apply visibility filtering based on authentication and user permissions
        if not self.request.user.is_authenticated:
            # Unauthenticated users can only see public RFQs
            queryset = queryset.filter(visibility='Public')
        elif self.request.user.id != int(user_id):
            # Authenticated users can see their own RFQs plus public RFQs from others
            queryset = queryset.filter(
                models.Q(visibility='Public') |
                models.Q(created_by_id=self.request.user.id)
            )

        return queryset.order_by('-created_at')

    def get_permissions(self):
        # Allow unauthenticated read-only access; write requires authentication
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class RFQReportView(APIView):
    """
    Report or unreport an RFQ for a user.
    POST /api/rfq/rfqs/report/
    Body: { "rfq_id": 123, "user": "user@example.com" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("DEBUG: RFQReportView.post called")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request content type: {request.content_type}")

        try:
            # Handle different content types - same logic as save view
            if 'text/plain' in request.content_type:
                # Parse JSON from text/plain request - read body directly
                import json
                print(f"DEBUG: Request body: {request.body}")
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    print("DEBUG: Parsed data from body:", data)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Invalid JSON in request body"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif request.content_type == 'application/json':
                # Use request.data for JSON requests
                print(f"DEBUG: Request data: {request.data}")
                data = request.data
            else:
                # For other content types, try request.data but don't access body
                print("DEBUG: Using request.data for other content types")
                data = request.data

            # Extract data from request
            rfq_id = data.get('rfq_id')
            user_email = data.get('user')
            print("DEBUG: rfq_id:", rfq_id)
            print("DEBUG: user_email:", user_email)

            if not rfq_id or not user_email:
                return Response(
                    {"error": "Both 'rfq_id' and 'user' are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the user
            print("DEBUG: Looking up user with email:", user_email)
            try:
                user = User.objects.get(email=user_email)
                print("DEBUG: User found:", user.id, user.email)
            except User.DoesNotExist:
                print("DEBUG: User not found with email:", user_email)
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the RFQ
            print("DEBUG: Looking up RFQ with id:", rfq_id)
            try:
                rfq = RFQ.objects.get(id=rfq_id)
                print("DEBUG: RFQ found:", rfq.id, rfq.title)
            except RFQ.DoesNotExist:
                print("DEBUG: RFQ not found with id:", rfq_id)
                return Response(
                    {"error": "RFQ not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if user already reported this RFQ
            print("DEBUG: Checking if user already reported this RFQ")
            is_reported = rfq.reported_by.filter(id=user.id).exists()
            print("DEBUG: is_reported:", is_reported)

            if is_reported:
                # Unreport the RFQ
                print("DEBUG: Unreporting RFQ")
                rfq.reported_by.remove(user)
                action = "unreported"
                message = f"RFQ {rfq_id} unreported successfully"
                print("DEBUG: RFQ unreported successfully")
            else:
                # Report the RFQ
                print("DEBUG: Reporting RFQ")
                rfq.reported_by.add(user)
                action = "reported"
                message = f"RFQ {rfq_id} reported successfully"
                print("DEBUG: RFQ reported successfully")

            return Response({
                "rfq_id": rfq_id,
                "user": user_email,
                "action": action,
                "message": message,
                "reported_count": rfq.reported_by.count()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"DEBUG: Error occurred: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RFQReportedByListView(APIView):
    """
    Get a list of all RFQs that have been reported by any users.
    GET /api/rfq/rfqs/reported-by-list/
    Returns a mapping of RFQ IDs to user IDs who reported them.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Return a mapping of RFQ IDs to user IDs who reported them
        """
        try:
            # Get all RFQs that have been reported (have users in reported_by field)
            # This returns RFQs reported by ANY user, not just the current user
            reported_rfqs = RFQ.objects.filter(reported_by__isnull=False).distinct()
            
            # Create a simple mapping of RFQ ID to list of user IDs who reported it
            rfq_user_mapping = {}
            for rfq in reported_rfqs:
                rfq_user_mapping[rfq.id] = list(rfq.reported_by.values_list('id', flat=True))
            
            return Response({
                "rfq_user_mapping": rfq_user_mapping,
                "total_reported_rfqs": len(rfq_user_mapping),
                "message": "Returns mapping of RFQ IDs to user IDs who reported them"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Error in RFQReportedByListView: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )