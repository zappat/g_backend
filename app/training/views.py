from rest_framework import generics, permissions
from .models import TrainingCourse, TrainingCategory
from .serializers import TrainingCourseSerializer, TrainingCategorySerializer

class TrainingCourseListCreateView(generics.ListCreateAPIView):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TrainingCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TrainingCategoryListCreateView(generics.ListCreateAPIView):
    queryset = TrainingCategory.objects.all()
    serializer_class = TrainingCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TrainingCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainingCategory.objects.all()
    serializer_class = TrainingCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 