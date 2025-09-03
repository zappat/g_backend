from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import os
from .models import Document
from .serializers import DocumentSerializer


class DocumentListCreateView(generics.ListCreateAPIView):
    """
    List all documents for the authenticated user or create new documents.
    GET /api/document-vault/documents/ - List user's documents
    POST /api/document-vault/documents/ - Upload new documents
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Return only documents belonging to the authenticated user"""
        return Document.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
    def create(self, request, *args, **kwargs):
        """Handle multiple file uploads"""
        try:
            # Handle multiple files from 'documents' field
            files = request.FILES.getlist('documents')
            
            if not files:
                return Response(
                    {"error": "No files provided. Use 'documents' field for file uploads."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_documents = []
            errors = []
            
            for file in files:
                try:
                    # Create document data
                    document_data = {
                        'file': file,
                        'name': file.name  # Use original filename as name
                    }
                    
                    # Serialize and validate
                    serializer = self.get_serializer(data=document_data)
                    if serializer.is_valid():
                        document = serializer.save()
                        uploaded_documents.append(serializer.data)
                    else:
                        errors.append({
                            'file': file.name,
                            'errors': serializer.errors
                        })
                        
                except Exception as e:
                    errors.append({
                        'file': file.name,
                        'error': str(e)
                    })
            
            # Prepare response
            response_data = {
                'uploaded_documents': uploaded_documents,
                'total_uploaded': len(uploaded_documents),
                'total_files': len(files)
            }
            
            if errors:
                response_data['errors'] = errors
                response_data['message'] = f"Uploaded {len(uploaded_documents)} out of {len(files)} files"
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            else:
                response_data['message'] = f"Successfully uploaded {len(uploaded_documents)} files"
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {"error": f"An error occurred during upload: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete a specific document.
    GET /api/document-vault/documents/{id}/ - Get document details
    DELETE /api/document-vault/documents/{id}/ - Delete document
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only documents belonging to the authenticated user"""
        return Document.objects.filter(user=self.request.user)


class DocumentDownloadView(APIView):
    """
    Download a specific document file.
    GET /api/document-vault/documents/{id}/download/ - Download document file
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Download the document file"""
        try:
            # Get the document, ensuring it belongs to the authenticated user
            document = get_object_or_404(Document, pk=pk, user=request.user)
            
            # Check if the file exists
            if not document.file or not document.file.name:
                return Response(
                    {"error": "File not found or has been deleted"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if file exists on storage
            if not document.file.storage.exists(document.file.name):
                return Response(
                    {"error": "File not found on storage"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get file content
            try:
                file_content = document.file.read()
            except Exception as e:
                return Response(
                    {"error": f"Error reading file: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Get filename for download
            filename = document.name or os.path.basename(document.file.name)
            
            # Create HTTP response with file content
            response = HttpResponse(file_content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(file_content)
            
            return response
            
        except Http404:
            return Response(
                {"error": "Document not found or you don't have permission to access it"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during download: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )