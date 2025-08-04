from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TrainingCourse, TrainingCategory
from .serializers import TrainingCourseListSerializer, TrainingCourseCreateSerializer, TrainingCategorySerializer

class TrainingCourseListCreateView(generics.ListCreateAPIView):
    queryset = TrainingCourse.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TrainingCourseListSerializer
        return TrainingCourseCreateSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"📝 Training course creation - Received data: {request.data}")
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print(f"❌ Training course validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print(f"✅ Training course data is valid")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ Training course creation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TrainingCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TrainingCategoryListCreateView(generics.ListCreateAPIView):
    queryset = TrainingCategory.objects.all()
    serializer_class = TrainingCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TrainingCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainingCategory.objects.all()
    serializer_class = TrainingCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

class TrainingCourseDeleteView(generics.DestroyAPIView):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TrainingCourseToggleVisibilityView(APIView):
    """Toggle the public/private state of a training course"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        return self._toggle_visibility(request, pk)
    
    def patch(self, request, pk):
        return self._toggle_visibility(request, pk)
    
    def _toggle_visibility(self, request, pk):
        try:
            # Get the training course
            training_course = TrainingCourse.objects.get(pk=pk)
            
            # Toggle the is_public field
            training_course.is_public = not training_course.is_public
            training_course.save()
            
            # Return the updated course data
            serializer = TrainingCourseListSerializer(training_course)
            return Response({
                "message": f"Course visibility toggled to {'public' if training_course.is_public else 'private'}",
                "course": serializer.data
            }, status=status.HTTP_200_OK)
            
        except TrainingCourse.DoesNotExist:
            return Response(
                {"error": "Training course not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )