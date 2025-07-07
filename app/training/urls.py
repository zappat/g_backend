from django.urls import path
from .views import (
    TrainingCourseListCreateView, TrainingCourseDetailView,
    TrainingCategoryListCreateView, TrainingCategoryDetailView
)

urlpatterns = [
    path('courses/', TrainingCourseListCreateView.as_view(), name='trainingcourse-list-create'),
    path('courses/<int:pk>/', TrainingCourseDetailView.as_view(), name='trainingcourse-detail'),
    path('categories/', TrainingCategoryListCreateView.as_view(), name='trainingcategory-list-create'),
    path('categories/<int:pk>/', TrainingCategoryDetailView.as_view(), name='trainingcategory-detail'),
] 